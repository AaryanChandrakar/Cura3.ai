"""
Cura3.ai — Chat Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """A single message in a chat session."""
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """User's follow-up question."""
    message: str


class ChatSessionInDB(BaseModel):
    """Chat session document stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    diagnosis_id: str
    messages: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ChatSessionResponse(BaseModel):
    """Chat session data returned to client."""
    id: str
    diagnosis_id: str
    messages: List[dict]
    created_at: datetime
    updated_at: datetime
