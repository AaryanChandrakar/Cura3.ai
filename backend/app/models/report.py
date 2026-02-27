"""
Cura3.ai — Report Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ReportUpload(BaseModel):
    """Report submitted via text input."""
    patient_name: Optional[str] = "Unknown Patient"
    content: str
    store_report: bool = True  # User chooses to store or discard


class ReportInDB(BaseModel):
    """Report document stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    patient_name: str = "Unknown Patient"
    filename: Optional[str] = None
    content: str
    source: Literal["upload", "text"] = "text"
    store_report: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ReportResponse(BaseModel):
    """Report data returned to the client."""
    id: str
    user_id: str
    patient_name: str
    filename: Optional[str] = None
    source: str
    store_report: bool
    created_at: datetime
    # Content excluded by default for list views (can be fetched individually)


class ReportDetail(ReportResponse):
    """Full report data including content."""
    content: str
