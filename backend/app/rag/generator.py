import json
import logging
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.rag.prompt_templates import get_system_prompt
from app.rag.guardrail import guardrail

logger = logging.getLogger(__name__)

class GroundedGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY,
            base_url=settings.GROK_API_BASE_URL
        )

    async def generate_stream(
        self, 
        query: str, 
        query_type: str, 
        context_docs: List[Dict[str, Any]], 
        chat_history: str
    ) -> AsyncGenerator[str, None]:
        """
        Generates a response using GROK LLM and streams chunks back.
        Applies guardrail after completion (if it fails, the client might have already seen bad text, 
        but we can yield a correction or we can just buffer it if we want strict guardrailing).
        For true streaming, we stream first, then guardrail. 
        If strict guardrailing is required, we shouldn't stream, or we stream and append a retraction.
        Given it's a financial app, we will generate the full response, guardrail it, and then yield it 
        in chunks to simulate streaming for UI consistency, or just return it.
        Let's buffer it, guardrail it, then yield.
        """
        
        # 1. Format context
        context_text = ""
        for i, doc in enumerate(context_docs):
            source_type = doc['metadata'].get('source_type', 'unknown')
            context_text += f"--- Source {i+1} ({source_type}) ---\n"
            context_text += doc['content'] + "\n\n"
            
        if not context_docs:
            context_text = "No relevant context found in the database."

        # 2. Get system prompt
        system_prompt = get_system_prompt(query_type, context_text, chat_history)
        
        if not settings.GROK_API_KEY:
            yield "Currently I don't have the data to answer the query (API Key missing)."
            return

        try:
            # 3. Call GROK
            response = await self.client.chat.completions.create(
                model=settings.GROK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.2, # Low temp for factual responses
                stream=False     # Buffer for guardrailing
            )
            
            full_response = response.choices[0].message.content.strip()
            
            # 4. Guardrail
            is_valid, final_response = guardrail.validate(full_response, context_text)
            
            # 5. Yield chunk (we just yield the whole thing for now, UI can handle it or we chunk it here)
            # To satisfy websocket streaming expectation:
            chunk_size = 50
            for i in range(0, len(final_response), chunk_size):
                yield final_response[i:i+chunk_size]
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            yield "Currently I don't have the data to answer the query due to a temporary error."

generator = GroundedGenerator()
