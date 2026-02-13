"""
GetStats query — returns dashboard analytics data.
Aggregates from daily_stats table + live counts.
"""

from dataclasses import dataclass

from sqlalchemy import func, select

from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import async_session
from app.features.analytics.models import DailyStats, PageVisit
from app.features.contact.models import ContactMessage
from app.features.ai_chat.models import ChatSession
from app.shared.mediator import Query, register_query_handler

CACHE_KEY = "analytics:dashboard"
CACHE_TTL = 60  # 1 minute — near real-time


@dataclass(frozen=True)
class GetStatsQuery(Query):
    days: int = 30


async def handle_get_stats(query: GetStatsQuery) -> dict:
    cached = await cache_get(CACHE_KEY)
    if cached:
        return cached

    async with async_session() as session:
        # Total visits
        total_visits_result = await session.execute(select(func.count(PageVisit.id)))
        total_visits = total_visits_result.scalar() or 0

        # Unique visitors
        unique_result = await session.execute(
            select(func.count(func.distinct(PageVisit.visitor_id)))
        )
        unique_visitors = unique_result.scalar() or 0

        # Total contact messages
        msg_result = await session.execute(select(func.count(ContactMessage.id)))
        total_messages = msg_result.scalar() or 0

        # Total chat sessions
        chat_result = await session.execute(select(func.count(ChatSession.id)))
        total_chats = chat_result.scalar() or 0

        # Daily stats (last N days)
        daily_result = await session.execute(
            select(DailyStats)
            .order_by(DailyStats.date.desc())
            .limit(query.days)
        )
        daily_stats = [
            {
                "date": str(d.date),
                "total_visits": d.total_visits,
                "unique_visitors": d.unique_visitors,
                "top_page": d.top_page,
                "contact_messages": d.contact_messages,
                "chat_sessions": d.chat_sessions,
            }
            for d in daily_result.scalars().all()
        ]

        # Top pages
        top_pages_result = await session.execute(
            select(PageVisit.path, func.count(PageVisit.id).label("count"))
            .group_by(PageVisit.path)
            .order_by(func.count(PageVisit.id).desc())
            .limit(10)
        )
        top_pages = [
            {"path": row.path, "count": row.count}
            for row in top_pages_result
        ]

        data = {
            "total_visits": total_visits,
            "unique_visitors": unique_visitors,
            "total_messages": total_messages,
            "total_chats": total_chats,
            "daily_stats": daily_stats,
            "top_pages": top_pages,
        }

        await cache_set(CACHE_KEY, data, CACHE_TTL)
        return data


register_query_handler(GetStatsQuery, handle_get_stats)
