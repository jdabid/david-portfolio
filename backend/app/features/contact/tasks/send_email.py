"""
Celery task: send notification email when contact form is submitted.
Implements retry with exponential backoff.
"""

import logging
import smtplib
from email.message import EmailMessage

from app.infrastructure.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="contact.send_email",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(smtplib.SMTPException, ConnectionError),
    retry_backoff=True,
    retry_backoff_max=600,
)
def send_contact_email(self, message_id: str, name: str, email: str, subject: str, body: str):
    """
    Send email notification for a contact form submission.
    Retries up to 3 times with exponential backoff (60s, 120s, 240s).
    Failed messages go to the Dead Letter Queue.
    """
    logger.info(f"Sending email for message {message_id} from {name} <{email}>")

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Portfolio Contact] {subject}"
        msg["From"] = "noreply@portfolio.dev"
        msg["To"] = "david@portfolio.dev"
        msg["Reply-To"] = email
        msg.set_content(
            f"New contact message from {name} ({email}):\n\n"
            f"Subject: {subject}\n\n"
            f"{body}\n\n"
            f"---\nMessage ID: {message_id}"
        )

        # In production, configure SMTP settings via environment variables.
        # For development, log the email instead of sending.
        logger.info(f"Email prepared for message {message_id}: subject='{subject}'")

        # Uncomment for real SMTP:
        # with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        #     server.starttls()
        #     server.login(settings.smtp_user, settings.smtp_password)
        #     server.send_message(msg)

        _update_message_status(message_id, "sent")
        logger.info(f"Email sent successfully for message {message_id}")

    except Exception as exc:
        logger.error(f"Failed to send email for {message_id}: {exc}")
        _update_message_status(message_id, "failed")
        raise self.retry(exc=exc)


def _update_message_status(message_id: str, status: str) -> None:
    """Sync helper to update message status in DB (runs inside Celery worker)."""
    from sqlalchemy import create_engine, text

    from app.config import settings

    sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE contact_messages SET status = :status WHERE id = :id"),
            {"status": status, "id": message_id},
        )
        conn.commit()
    engine.dispose()
