"""
Contact message model.
Stores contact form submissions with processing status.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDMixin


class ContactMessage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "contact_messages"

    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(254))
    subject: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, sent, failed
