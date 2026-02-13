"""
Analytics API endpoints.
"""

from fastapi import APIRouter, Request

from app.features.analytics.schemas import TrackVisitRequest, DashboardResponse
from app.features.analytics.commands.track_visit import TrackVisitCommand
from app.features.analytics.queries.get_stats import GetStatsQuery
from app.shared.mediator import send_command, send_query

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/track", status_code=204)
async def track_visit(body: TrackVisitRequest, request: Request):
    """Track a page visit. Called by frontend on route change."""
    await send_command(
        TrackVisitCommand(
            path=body.path,
            visitor_id=body.visitor_id,
            user_agent=body.user_agent,
            referrer=body.referrer,
            ip_address=request.client.host if request.client else "",
        )
    )
    return None


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(days: int = 30):
    """Get analytics dashboard data. Admin endpoint."""
    return await send_query(GetStatsQuery(days=days))
