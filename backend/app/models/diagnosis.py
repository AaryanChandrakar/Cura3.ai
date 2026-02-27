"""
Cura3.ai — Diagnosis Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class SpecialistReport(BaseModel):
    """Individual specialist's analysis report."""
    specialist_name: str
    report_content: str


class DiagnosisRequest(BaseModel):
    """Request to run a diagnosis on a report."""
    report_id: str
    selected_specialists: Optional[List[str]] = None  # None = auto-select


class DiagnosisInDB(BaseModel):
    """Diagnosis document stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    report_id: str
    selected_specialists: List[str]
    specialist_reports: List[Dict[str, str]]  # [{name, content}, ...]
    final_diagnosis: str
    status: str = "completed"  # pending | processing | completed | failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DiagnosisResponse(BaseModel):
    """Diagnosis summary returned in list views."""
    id: str
    user_id: str
    report_id: str
    selected_specialists: List[str]
    status: str
    created_at: datetime


class DiagnosisDetail(DiagnosisResponse):
    """Full diagnosis data including all reports."""
    specialist_reports: List[Dict[str, str]]
    final_diagnosis: str
