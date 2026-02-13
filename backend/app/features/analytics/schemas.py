"""
Analytics Pydantic schemas.
"""

from pydantic import BaseModel


class TrackVisitRequest(BaseModel):
    path: str
    visitor_id: str = "anonymous"
    user_agent: str = ""
    referrer: str = ""


class DailyStatsResponse(BaseModel):
    date: str
    total_visits: int
    unique_visitors: int
    top_page: str
    contact_messages: int
    chat_sessions: int

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    total_visits: int
    unique_visitors: int
    total_messages: int
    total_chats: int
    daily_stats: list[DailyStatsResponse]
    top_pages: list[dict]
