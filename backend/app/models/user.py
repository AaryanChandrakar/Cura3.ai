"""
Cura3.ai — User Data Models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class UserCreate(BaseModel):
    """Data received from Google OAuth."""
    email: EmailStr
    name: str
    google_id: str
    avatar_url: Optional[str] = None


class UserInDB(BaseModel):
    """User document stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    email: str
    name: str
    google_id: str
    avatar_url: Optional[str] = None
    role: Literal["patient", "doctor", "admin"] = "patient"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """User data returned to the client."""
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields that can be updated by the user."""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
