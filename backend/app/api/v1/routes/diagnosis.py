"""
Cura3.ai — Diagnosis Routes
Run AI diagnosis, view results, download PDF, manage history.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.responses import StreamingResponse
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_database
from app.core.security import get_current_user
from app.services.agent_engine import run_diagnosis, AVAILABLE_SPECIALISTS
from app.services.specialist_selector import auto_select_specialists

router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])


class DiagnosisRequest(BaseModel):
    report_id: str
    selected_specialists: Optional[list[str]] = None


@router.get("/specialists")
async def list_specialists():
    """List all available medical specialists."""
    from app.services.agent_engine import SPECIALISTS

    specialists = []
    for name, info in SPECIALISTS.items():
        specialists.append({
            "name": name,
            "display_name": info["display_name"],
            "icon": info["icon"],
        })
    return {"specialists": specialists, "total": len(specialists)}


@router.post("/auto-select/{report_id}")
async def auto_select(report_id: str, current_user: dict = Depends(get_current_user)):
    """Auto-select the best specialists for a given report using AI."""
    db = get_database()

    try:
        report = await db.reports.find_one({
            "_id": ObjectId(report_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID.")

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    recommended = await auto_select_specialists(report["content"])

    return {
        "report_id": report_id,
        "recommended_specialists": recommended,
        "all_available": AVAILABLE_SPECIALISTS,
    }


@router.post("/run")
async def run_diagnosis_endpoint(
    request: DiagnosisRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Run a full AI diagnosis on a medical report.

    If selected_specialists is not provided, auto-selects the best specialists.
    """
    db = get_database()
    report_id = request.report_id
    selected_specialists = request.selected_specialists

    # Get the report
    try:
        report = await db.reports.find_one({
            "_id": ObjectId(report_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID.")

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    # Auto-select specialists if none provided
    if not selected_specialists:
        selected_specialists = await auto_select_specialists(report["content"])

    # Validate specialist names
    invalid = [s for s in selected_specialists if s not in AVAILABLE_SPECIALISTS]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid specialists: {invalid}. Available: {AVAILABLE_SPECIALISTS}",
        )

    # Run the diagnosis
    result = await run_diagnosis(report["content"], selected_specialists)

    # Store in MongoDB
    diagnosis_doc = {
        "user_id": current_user["_id"],
        "report_id": report_id,
        "patient_name": report.get("patient_name", "Unknown"),
        "selected_specialists": selected_specialists,
        "specialist_reports": result["specialist_reports"],
        "final_diagnosis": result["final_diagnosis"],
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
    }
    insert_result = await db.diagnoses.insert_one(diagnosis_doc)

    # Track analytics
    await db.analytics.insert_one({
        "event_type": "diagnosis_completed",
        "user_id": current_user["_id"],
        "diagnosis_id": str(insert_result.inserted_id),
        "specialists_used": selected_specialists,
        "timestamp": datetime.now(timezone.utc),
    })

    return {
        "id": str(insert_result.inserted_id),
        "report_id": report_id,
        "selected_specialists": selected_specialists,
        "specialist_reports": result["specialist_reports"],
        "final_diagnosis": result["final_diagnosis"],
        "status": "completed",
        "created_at": diagnosis_doc["created_at"],
    }


@router.get("/history")
async def diagnosis_history(current_user: dict = Depends(get_current_user)):
    """Get all past diagnoses for the current user."""
    db = get_database()
    cursor = db.diagnoses.find(
        {"user_id": current_user["_id"]}
    ).sort("created_at", -1)

    diagnoses = []
    async for doc in cursor:
        diagnoses.append({
            "id": str(doc["_id"]),
            "report_id": doc.get("report_id"),
            "patient_name": doc.get("patient_name", "Unknown"),
            "selected_specialists": doc.get("selected_specialists", []),
            "status": doc.get("status", "completed"),
            "created_at": doc.get("created_at"),
        })

    return {"diagnoses": diagnoses, "total": len(diagnoses)}


@router.get("/{diagnosis_id}")
async def get_diagnosis(diagnosis_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific diagnosis with full details."""
    db = get_database()

    try:
        doc = await db.diagnoses.find_one({
            "_id": ObjectId(diagnosis_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diagnosis ID.")

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    return {
        "id": str(doc["_id"]),
        "report_id": doc.get("report_id"),
        "patient_name": doc.get("patient_name", "Unknown"),
        "selected_specialists": doc.get("selected_specialists", []),
        "specialist_reports": doc.get("specialist_reports", []),
        "final_diagnosis": doc.get("final_diagnosis", ""),
        "status": doc.get("status", "completed"),
        "created_at": doc.get("created_at"),
    }


@router.get("/{diagnosis_id}/pdf")
async def download_diagnosis_pdf(diagnosis_id: str, current_user: dict = Depends(get_current_user)):
    """Download a diagnosis as a professionally formatted PDF report."""
    db = get_database()

    try:
        doc = await db.diagnoses.find_one({
            "_id": ObjectId(diagnosis_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diagnosis ID.")

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    from app.services.pdf_generator import generate_diagnosis_pdf
    import io

    pdf_bytes = await generate_diagnosis_pdf(
        patient_name=doc.get("patient_name", "Unknown"),
        specialists=doc.get("selected_specialists", []),
        specialist_reports=doc.get("specialist_reports", []),
        final_diagnosis=doc.get("final_diagnosis", ""),
        created_at=doc.get("created_at"),
    )

    patient = doc.get("patient_name", "diagnosis").replace(" ", "_")
    filename = f"Cura3ai_Report_{patient}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{diagnosis_id}")
async def delete_diagnosis(diagnosis_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a specific diagnosis."""
    db = get_database()

    try:
        result = await db.diagnoses.delete_one({
            "_id": ObjectId(diagnosis_id),
            "user_id": current_user["_id"],
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diagnosis ID.")

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")

    # Also delete associated chat sessions
    await db.chat_sessions.delete_many({"diagnosis_id": diagnosis_id})

    return {"message": "Diagnosis and associated chat sessions deleted successfully."}
