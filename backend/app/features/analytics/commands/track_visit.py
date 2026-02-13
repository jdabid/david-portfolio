"""
TrackVisit command — records a page visit for analytics.
Lightweight write; aggregation is done by Celery Beat.
"""

from dataclasses import dataclass

from app.infrastructure.database import async_session
from app.features.analytics.models import PageVisit
from app.shared.mediator import Command, register_command_handler


@dataclass(frozen=True)
class TrackVisitCommand(Command):
    path: str
    visitor_id: str = "anonymous"
    user_agent: str = ""
    referrer: str = ""
    ip_address: str = ""


async def handle_track_visit(command: TrackVisitCommand) -> dict:
    async with async_session() as session:
        visit = PageVisit(
            path=command.path,
            visitor_id=command.visitor_id,
            user_agent=command.user_agent,
            referrer=command.referrer,
            ip_address=command.ip_address,
        )
        session.add(visit)
        await session.commit()
        return {"tracked": True}


register_command_handler(TrackVisitCommand, handle_track_visit)
