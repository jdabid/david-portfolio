"""
Analytics domain models.
Tracks page visits and aggregated daily stats.
"""

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDMixin


class PageVisit(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "page_visits"

    path: Mapped[str] = mapped_column(String(500))
    visitor_id: Mapped[str] = mapped_column(String(100), index=True)
    user_agent: Mapped[str] = mapped_column(String(500), default="")
    referrer: Mapped[str] = mapped_column(String(500), default="")
    ip_address: Mapped[str] = mapped_column(String(45), default="")


class DailyStats(UUIDMixin, Base):
    __tablename__ = "daily_stats"

    date: Mapped[str] = mapped_column(Date, unique=True, index=True)
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    top_page: Mapped[str] = mapped_column(String(500), default="")
    contact_messages: Mapped[int] = mapped_column(Integer, default=0)
    chat_sessions: Mapped[int] = mapped_column(Integer, default=0)
