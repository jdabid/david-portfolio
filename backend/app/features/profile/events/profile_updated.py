"""
ProfileUpdated domain event — published to RabbitMQ when profile data changes.
Consumed by cache invalidation worker.
"""

from dataclasses import dataclass

from app.shared.event_bus import DomainEvent, publish_event


@dataclass
class ProfileUpdatedEvent(DomainEvent):
    event_type: str = "profile.updated"
    profile_id: str = ""


async def emit_profile_updated(profile_id: str) -> None:
    event = ProfileUpdatedEvent(profile_id=profile_id)
    await publish_event(event, routing_key="profile.updated")
