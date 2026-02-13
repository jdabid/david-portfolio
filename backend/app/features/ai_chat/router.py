"""
AI Chat endpoints — REST for sync chat + WebSocket for streaming.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from app.features.ai_chat.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from app.features.ai_chat.commands.send_chat import SendChatCommand
from app.features.ai_chat.queries.get_chat_history import GetChatHistoryQuery
from app.features.ai_chat.services.llm_service import stream_response
from app.features.ai_chat.models import ChatMessage, ChatSession
from app.infrastructure.database import async_session
from app.infrastructure.cache import cache_delete
from app.shared.mediator import send_command, send_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["ai_chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(body: ChatRequest):
    """Send a message and get a complete AI response (non-streaming)."""
    result = await send_command(
        SendChatCommand(message=body.message, session_id=body.session_id)
    )
    return result


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    result = await send_query(GetChatHistoryQuery(session_id=session_id))
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for streaming AI responses.

    Client sends: {"message": "...", "session_id": "..."}
    Server streams: {"type": "token", "content": "..."} per token
    Server ends with: {"type": "done", "session_id": "..."}
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_message = payload.get("message", "")
            session_id = payload.get("session_id")

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            # Load chat history for context
            chat_history = []
            if session_id:
                history = await send_query(GetChatHistoryQuery(session_id=session_id))
                if history:
                    chat_history = history.get("messages", [])

            # Persist user message
            async with async_session() as db:
                if not session_id:
                    chat_session = ChatSession(visitor_id="ws-visitor")
                    db.add(chat_session)
                    await db.flush()
                    session_id = str(chat_session.id)

                user_msg = ChatMessage(
                    session_id=session_id, role="user", content=user_message
                )
                db.add(user_msg)
                await db.commit()

            # Stream AI response
            full_response = []
            async for token in stream_response(user_message, chat_history):
                full_response.append(token)
                await websocket.send_json({"type": "token", "content": token})

            # Persist AI response
            ai_content = "".join(full_response)
            async with async_session() as db:
                ai_msg = ChatMessage(
                    session_id=session_id, role="assistant", content=ai_content
                )
                db.add(ai_msg)
                await db.commit()

            # Invalidate chat history cache
            await cache_delete(f"chat:history:{session_id}")

            await websocket.send_json({"type": "done", "session_id": session_id})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
