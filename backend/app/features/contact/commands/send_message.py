"""
SendMessage command — persists the contact message and publishes event to RabbitMQ.
The actual email is sent async by a Celery worker.
"""

from dataclasses import dataclass

from app.infrastructure.database import async_session
from app.features.contact.models import ContactMessage
from app.features.contact.events.message_received import emit_message_received
from app.shared.mediator import Command, register_command_handler


@dataclass(frozen=True)
class SendMessageCommand(Command):
    name: str
    email: str
    subject: str
    message: str


async def handle_send_message(command: SendMessageCommand) -> dict:
    async with async_session() as session:
        msg = ContactMessage(
            name=command.name,
            email=command.email,
            subject=command.subject,
            message=command.message,
            status="pending",
        )
        session.add(msg)
        await session.commit()
        await session.refresh(msg)

        # Publish domain event → RabbitMQ → Celery worker sends email
        await emit_message_received(
            message_id=str(msg.id),
            name=msg.name,
            email=msg.email,
            subject=msg.subject,
        )

        return {
            "id": str(msg.id),
            "status": "pending",
            "detail": "Message received. Email will be sent shortly.",
        }


register_command_handler(SendMessageCommand, handle_send_message)
