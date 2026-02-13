"""
MessageReceived domain event.
Published to RabbitMQ when a contact form is submitted.
Consumed by the Celery email worker.
"""

from dataclasses import dataclass

from app.shared.event_bus import DomainEvent, publish_event


@dataclass
class MessageReceivedEvent(DomainEvent):
    event_type: str = "contact.message.received"
    message_id: str = ""
    name: str = ""
    email: str = ""
    subject: str = ""


async def emit_message_received(
    message_id: str, name: str, email: str, subject: str
) -> None:
    event = MessageReceivedEvent(
        message_id=message_id,
        name=name,
        email=email,
        subject=subject,
    )
    await publish_event(event, routing_key="contact.message.received")
