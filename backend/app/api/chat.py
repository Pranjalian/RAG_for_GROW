import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.rag.query_classifier import query_classifier
from app.rag.retriever import retriever
from app.rag.generator import generator
from app.rag.conversation import conversation_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for the grounded chat interface.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")

    try:
        while True:
            # 1. Receive message from client
            # Format: { "type": "user_message", "content": "..." }
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_msg = payload.get("content", "").strip()
            except json.JSONDecodeError:
                continue

            if not user_msg:
                continue

            # Add to memory
            conversation_manager.add_user_message(session_id, user_msg)
            
            # 2. Classify query
            query_type = await query_classifier.classify(user_msg)
            logger.info(f"Classified query as: {query_type}")
            
            # 3. Fast-path advice rejection
            if query_type == "advice_request":
                decline_msg = "I am a factual data assistant and cannot provide investment advice. Please consult a financial advisor for recommendations."
                await websocket.send_text(json.dumps({
                    "type": "assistant_message",
                    "content": decline_msg,
                    "sources": [],
                    "done": True
                }))
                conversation_manager.add_assistant_message(session_id, decline_msg)
                continue
                
            # 4. Retrieve context
            context_docs = await retriever.retrieve(user_msg, query_type)
            
            # Prepare sources for final message
            sources = []
            seen_urls = set()
            for doc in context_docs:
                meta = doc.get("metadata", {})
                url = meta.get("url", "unknown")
                if url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "url": url,
                        "source_type": meta.get("source_type", "unknown"),
                        "last_updated": meta.get("last_updated", "unknown")
                    })
            
            # 5. Generate and stream
            chat_history = conversation_manager.get_history_string(session_id)
            
            final_content = ""
            async for chunk in generator.generate_stream(user_msg, query_type, context_docs, chat_history):
                # Stream chunk to client
                await websocket.send_text(json.dumps({
                    "type": "assistant_chunk",
                    "content": chunk,
                    "done": False
                }))
                final_content += chunk
                
            # 6. Send final completion message with sources
            await websocket.send_text(json.dumps({
                "type": "assistant_message",
                "content": "", # Content is already streamed, but UI might want the final trigger
                "sources": sources,
                "done": True
            }))
            
            # Add to memory
            conversation_manager.add_assistant_message(session_id, final_content)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "assistant_message",
                "content": "An internal error occurred. Please try again.",
                "sources": [],
                "done": True
            }))
        except:
            pass
