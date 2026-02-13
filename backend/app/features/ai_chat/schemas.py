"""
AI Chat Pydantic schemas.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessageResponse


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]
