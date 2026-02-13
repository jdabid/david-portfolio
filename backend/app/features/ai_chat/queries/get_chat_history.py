"""
GetChatHistory query — retrieves chat session messages.
Uses Redis cache with short TTL for active sessions.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.ai_chat.models import ChatSession
from app.shared.mediator import Query, register_query_handler

CACHE_TTL = 120  # 2 minutes — short TTL for active conversations


@dataclass(frozen=True)
class GetChatHistoryQuery(Query):
    session_id: str


async def handle_get_chat_history(query: GetChatHistoryQuery) -> dict | None:
    cache_key = f"chat:history:{query.session_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with async_session() as session:
        result = await session.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == query.session_id)
        )
        chat_session = result.scalar_one_or_none()
        if not chat_session:
            return None

        data = {
            "session_id": str(chat_session.id),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": str(msg.created_at),
                }
                for msg in chat_session.messages
            ],
        }

        await cache_set(cache_key, data, CACHE_TTL)
        return data


register_query_handler(GetChatHistoryQuery, handle_get_chat_history)
