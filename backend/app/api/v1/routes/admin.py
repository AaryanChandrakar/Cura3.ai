"""
Cura3.ai — Admin Routes
Admin-only endpoints for user management, system monitoring, audit logs, and API usage.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from app.core.database import get_database
from app.core.security import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def list_users(current_user: dict = Depends(require_role("admin"))):
    """List all users (admin only)."""
    db = get_database()
    cursor = db.users.find({}).sort("created_at", -1)

    users = []
    async for doc in cursor:
        users.append({
            "id": str(doc["_id"]),
            "email": doc.get("email"),
            "name": doc.get("name"),
            "role": doc.get("role", "patient"),
            "is_active": doc.get("is_active", True),
            "created_at": doc.get("created_at"),
        })

    return {"users": users, "total": len(users)}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    current_user: dict = Depends(require_role("admin")),
):
    """Update a user's role (admin only)."""
    if role not in ("patient", "doctor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: patient, doctor, or admin.",
        )

    db = get_database()
    try:
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": role}},
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID.")

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {"message": f"User role updated to '{role}'."}


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin")),
):
    """Deactivate a user account (admin only)."""
    db = get_database()
    try:
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}},
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID.")

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {"message": "User deactivated successfully."}


@router.get("/stats")
async def system_stats(current_user: dict = Depends(require_role("admin"))):
    """Get system-wide statistics (admin only)."""
    db = get_database()

    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    total_reports = await db.reports.count_documents({})
    total_diagnoses = await db.diagnoses.count_documents({})
    total_chats = await db.chat_sessions.count_documents({})

    # Role distribution
    patient_count = await db.users.count_documents({"role": "patient"})
    doctor_count = await db.users.count_documents({"role": "doctor"})
    admin_count = await db.users.count_documents({"role": "admin"})

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "patients": patient_count,
            "doctors": doctor_count,
            "admins": admin_count,
        },
        "reports": {"total": total_reports},
        "diagnoses": {"total": total_diagnoses},
        "chat_sessions": {"total": total_chats},
    }


# ── Audit Logs ───────────────────────────────────────────

@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    path_contains: Optional[str] = Query(None, description="Filter by path substring"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    current_user: dict = Depends(require_role("admin")),
):
    """Get paginated audit log entries (admin only)."""
    db = get_database()

    # Build filter
    query = {}
    if method:
        query["method"] = method.upper()
    if path_contains:
        query["path"] = {"$regex": path_contains, "$options": "i"}
    if status_code:
        query["status_code"] = status_code

    skip = (page - 1) * limit
    total = await db.audit_logs.count_documents(query)

    cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    logs = []
    async for doc in cursor:
        logs.append({
            "id": str(doc["_id"]),
            "timestamp": doc.get("timestamp"),
            "method": doc.get("method"),
            "path": doc.get("path"),
            "status_code": doc.get("status_code"),
            "duration_ms": doc.get("duration_ms"),
            "client_ip": doc.get("client_ip"),
            "user_hint": doc.get("user_hint"),
        })

    return {
        "logs": logs,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }


# ── API Usage Monitoring ─────────────────────────────────

@router.get("/api-usage")
async def get_api_usage(
    hours: int = Query(24, ge=1, le=720, description="Hours to look back"),
    current_user: dict = Depends(require_role("admin")),
):
    """Get API usage statistics aggregated by endpoint (admin only)."""
    db = get_database()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Aggregate usage by endpoint
    pipeline = [
        {"$match": {"hour_bucket": {"$gte": cutoff}}},
        {
            "$group": {
                "_id": "$endpoint",
                "total_requests": {"$sum": "$request_count"},
                "total_duration_ms": {"$sum": "$total_duration_ms"},
                "min_duration_ms": {"$min": "$min_duration_ms"},
                "max_duration_ms": {"$max": "$max_duration_ms"},
            }
        },
        {"$sort": {"total_requests": -1}},
        {"$limit": 50},
    ]

    endpoints = []
    async for doc in db.api_usage.aggregate(pipeline):
        avg_duration = (
            round(doc["total_duration_ms"] / doc["total_requests"], 2)
            if doc["total_requests"] > 0
            else 0
        )
        endpoints.append({
            "endpoint": doc["_id"],
            "total_requests": doc["total_requests"],
            "avg_duration_ms": avg_duration,
            "min_duration_ms": doc.get("min_duration_ms", 0),
            "max_duration_ms": doc.get("max_duration_ms", 0),
        })

    # Hourly request counts (for time-series chart)
    hourly_pipeline = [
        {"$match": {"hour_bucket": {"$gte": cutoff}}},
        {
            "$group": {
                "_id": "$hour_bucket",
                "requests": {"$sum": "$request_count"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    hourly_data = []
    async for doc in db.api_usage.aggregate(hourly_pipeline):
        hourly_data.append({
            "hour": doc["_id"].isoformat() if doc["_id"] else None,
            "requests": doc["requests"],
        })

    # Total summary
    total_requests = sum(e["total_requests"] for e in endpoints)

    return {
        "period_hours": hours,
        "total_requests": total_requests,
        "endpoints": endpoints,
        "hourly_requests": hourly_data,
    }
