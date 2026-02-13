"""
Celery task: aggregate daily analytics metrics.
Scheduled by Celery Beat to run every hour.
"""

import logging
from datetime import date, datetime, timezone

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="analytics.aggregate_daily")
def aggregate_daily_metrics():
    """
    Aggregate page visits into daily_stats table.
    Runs hourly via Celery Beat — updates today's row each run.
    """
    sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_url)

    today = date.today()

    with engine.connect() as conn:
        # Count today's visits
        result = conn.execute(
            text(
                "SELECT COUNT(*) as total, COUNT(DISTINCT visitor_id) as unique_v "
                "FROM page_visits WHERE DATE(created_at) = :today"
            ),
            {"today": today},
        )
        row = result.fetchone()
        total_visits = row.total if row else 0
        unique_visitors = row.unique_v if row else 0

        # Top page today
        top_result = conn.execute(
            text(
                "SELECT path, COUNT(*) as cnt FROM page_visits "
                "WHERE DATE(created_at) = :today "
                "GROUP BY path ORDER BY cnt DESC LIMIT 1"
            ),
            {"today": today},
        )
        top_row = top_result.fetchone()
        top_page = top_row.path if top_row else "/"

        # Contact messages today
        msg_result = conn.execute(
            text(
                "SELECT COUNT(*) FROM contact_messages WHERE DATE(created_at) = :today"
            ),
            {"today": today},
        )
        contact_messages = msg_result.scalar() or 0

        # Chat sessions today
        chat_result = conn.execute(
            text(
                "SELECT COUNT(*) FROM chat_sessions WHERE DATE(created_at) = :today"
            ),
            {"today": today},
        )
        chat_sessions = chat_result.scalar() or 0

        # Upsert daily_stats
        conn.execute(
            text(
                "INSERT INTO daily_stats (id, date, total_visits, unique_visitors, top_page, contact_messages, chat_sessions) "
                "VALUES (gen_random_uuid(), :date, :total, :unique, :top_page, :msgs, :chats) "
                "ON CONFLICT (date) DO UPDATE SET "
                "total_visits = :total, unique_visitors = :unique, top_page = :top_page, "
                "contact_messages = :msgs, chat_sessions = :chats"
            ),
            {
                "date": today,
                "total": total_visits,
                "unique": unique_visitors,
                "top_page": top_page,
                "msgs": contact_messages,
                "chats": chat_sessions,
            },
        )
        conn.commit()

    engine.dispose()
    logger.info(
        f"Aggregated daily metrics for {today}: "
        f"{total_visits} visits, {unique_visitors} unique, top={top_page}"
    )
