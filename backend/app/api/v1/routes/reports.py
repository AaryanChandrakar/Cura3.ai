"""
Cura3.ai — Report Management Routes
Upload, list, view, and delete medical reports.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Optional
from bson import ObjectId
from datetime import datetime, timezone
from app.core.database import get_database
from app.core.security import get_current_user
from app.services.report_parser import parse_report_file
from app.config import settings

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    patient_name: str = Form("Unknown Patient"),
    store_report: bool = Form(True),
    current_user: dict = Depends(get_current_user),
):
    """Upload a medical report file (.txt, .pdf, .docx)."""
    # Validate file extension
    filename = file.filename or "unknown.txt"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if f".{ext}" not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: .{ext}. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Validate file size
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Parse file content
    try:
        content = await parse_report_file(filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file appears to be empty or unreadable.",
        )

    # Store in MongoDB
    db = get_database()
    report_doc = {
        "user_id": current_user["_id"],
        "patient_name": patient_name,
        "filename": filename,
        "content": content,
        "source": "upload",
        "store_report": store_report,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.reports.insert_one(report_doc)

    return {
        "id": str(result.inserted_id),
        "message": "Report uploaded successfully.",
        "patient_name": patient_name,
        "filename": filename,
        "content_length": len(content),
    }


from pydantic import BaseModel as ReportBaseModel


class TextReportRequest(ReportBaseModel):
    content: str
    patient_name: Optional[str] = "Unknown Patient"
    store_report: bool = True


@router.post("/text")
async def submit_text_report(
    request: TextReportRequest,
    current_user: dict = Depends(get_current_user),
):
    """Submit a medical report as raw text."""
    if not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report content cannot be empty.",
        )

    db = get_database()
    report_doc = {
        "user_id": current_user["_id"],
        "patient_name": request.patient_name,
        "filename": None,
        "content": request.content,
        "source": "text",
        "store_report": request.store_report,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.reports.insert_one(report_doc)

    return {
        "id": str(result.inserted_id),
        "message": "Report submitted successfully.",
        "patient_name": request.patient_name,
        "content_length": len(request.content),
    }


@router.get("/")
async def list_reports(current_user: dict = Depends(get_current_user)):
    """List all reports for the current user."""
    db = get_database()
    cursor = db.reports.find(
        {"user_id": current_user["_id"], "store_report": True}
    ).sort("created_at", -1)

    reports = []
    async for doc in cursor:
        reports.append({
            "id": str(doc["_id"]),
            "patient_name": doc.get("patient_name", "Unknown"),
            "filename": doc.get("filename"),
            "source": doc.get("source", "text"),
            "created_at": doc.get("created_at"),
        })

    return {"reports": reports, "total": len(reports)}


@router.get("/{report_id}")
async def get_report(report_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific report with full content."""
    db = get_database()
    try:
        doc = await db.reports.find_one({
            "_id": ObjectId(report_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID.")

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    return {
        "id": str(doc["_id"]),
        "patient_name": doc.get("patient_name", "Unknown"),
        "filename": doc.get("filename"),
        "content": doc.get("content", ""),
        "source": doc.get("source", "text"),
        "store_report": doc.get("store_report", True),
        "created_at": doc.get("created_at"),
    }


@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a specific report (manual deletion for HIPAA compliance)."""
    db = get_database()
    try:
        result = await db.reports.delete_one({
            "_id": ObjectId(report_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID.")

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    # Also delete associated diagnoses and chat sessions
    await db.diagnoses.delete_many({"report_id": report_id})
    await db.chat_sessions.delete_many({"report_id": report_id})

    return {"message": "Report and associated data deleted successfully."}
