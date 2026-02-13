"""
SendChat command — processes a user message through the RAG pipeline.
Persists both user message and AI response in the chat history.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.database import async_session
from app.features.ai_chat.models import ChatMessage, ChatSession
from app.features.ai_chat.services.llm_service import generate_response
from app.shared.mediator import Command, register_command_handler


@dataclass(frozen=True)
class SendChatCommand(Command):
    message: str
    session_id: str | None = None
    visitor_id: str = "anonymous"


async def handle_send_chat(command: SendChatCommand) -> dict:
    async with async_session() as session:
        # Get or create chat session
        if command.session_id:
            result = await session.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.id == command.session_id)
            )
            chat_session = result.scalar_one_or_none()
        else:
            chat_session = None

        if not chat_session:
            chat_session = ChatSession(visitor_id=command.visitor_id)
            session.add(chat_session)
            await session.flush()

        # Build chat history for context
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in (chat_session.messages or [])
        ]

        # Save user message
        user_msg = ChatMessage(
            session_id=str(chat_session.id),
            role="user",
            content=command.message,
        )
        session.add(user_msg)

        # Generate AI response via RAG pipeline
        ai_content = await generate_response(command.message, chat_history)

        # Save AI response
        ai_msg = ChatMessage(
            session_id=str(chat_session.id),
            role="assistant",
            content=ai_content,
        )
        session.add(ai_msg)
        await session.commit()
        await session.refresh(ai_msg)

        return {
            "session_id": str(chat_session.id),
            "message": {
                "id": str(ai_msg.id),
                "role": "assistant",
                "content": ai_content,
                "created_at": str(ai_msg.created_at),
            },
        }


register_command_handler(SendChatCommand, handle_send_chat)
