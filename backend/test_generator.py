import asyncio
from app.rag.generator import generator
from app.rag.retriever import retriever
from app.rag.prompt_templates import get_system_prompt

async def test():
    query = "what is the fund price of hdfc large and mid cap"
    query_type = "fund_lookup"
    
    docs = await retriever.retrieve(query, query_type)
    
    context_text = ""
    for i, doc in enumerate(docs):
        source_type = doc['metadata'].get('source_type', 'unknown')
        context_text += f"--- Source {i+1} ({source_type}) ---\n"
        context_text += doc['content'] + "\n\n"
        
    system_prompt = get_system_prompt(query_type, context_text, "")
    
    from app.config import settings
    response = await generator.client.chat.completions.create(
        model=settings.GROK_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.2,
        stream=False
    )
    # Safely print ASCII by ignoring weird chars
    print("RAW RESPONSE:", response.choices[0].message.content.encode("ascii", "ignore").decode("ascii"))

asyncio.run(test())
