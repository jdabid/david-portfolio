"""
Contact API endpoints.
"""

from fastapi import APIRouter

from app.features.contact.schemas import SendMessageRequest
from app.features.contact.commands.send_message import SendMessageCommand
from app.shared.mediator import send_command

router = APIRouter(prefix="/api/contact", tags=["contact"])


@router.post("", status_code=202)
async def send_message(body: SendMessageRequest):
    """
    Submit a contact message.
    Returns 202 Accepted — email is processed async by Celery worker.
    """
    return await send_command(
        SendMessageCommand(
            name=body.name,
            email=body.email,
            subject=body.subject,
            message=body.message,
        )
    )
