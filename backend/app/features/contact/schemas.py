"""
Contact Pydantic schemas.
"""

from pydantic import BaseModel, EmailStr


class SendMessageRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str


class ContactMessageResponse(BaseModel):
    id: str
    name: str
    email: str
    subject: str
    message: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}
