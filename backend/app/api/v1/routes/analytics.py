"""
Cura3.ai — Analytics Routes
Usage statistics and tracking.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, timezone
from app.core.database import get_database
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/me")
async def my_analytics(current_user: dict = Depends(get_current_user)):
    """Get personal usage analytics for the current user."""
    db = get_database()
    user_id = current_user["_id"]

    total_reports = await db.reports.count_documents({"user_id": user_id})
    total_diagnoses = await db.diagnoses.count_documents({"user_id": user_id})
    total_chats = await db.chat_sessions.count_documents({"user_id": user_id})

    # Get specialist usage breakdown
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": "$selected_specialists"},
        {"$group": {"_id": "$selected_specialists", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    specialist_usage = []
    async for doc in db.diagnoses.aggregate(pipeline):
        specialist_usage.append({"specialist": doc["_id"], "count": doc["count"]})

    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_diagnoses = await db.diagnoses.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": thirty_days_ago},
    })

    return {
        "total_reports": total_reports,
        "total_diagnoses": total_diagnoses,
        "total_chats": total_chats,
        "specialist_usage": specialist_usage,
        "recent_diagnoses_30d": recent_diagnoses,
    }


@router.get("/global")
async def global_analytics(current_user: dict = Depends(require_role("admin"))):
    """Get global platform analytics (admin only)."""
    db = get_database()

    # Daily diagnosis counts for last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    pipeline = [
        {"$match": {"timestamp": {"$gte": thirty_days_ago}, "event_type": "diagnosis_completed"}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    daily_diagnoses = []
    async for doc in db.analytics.aggregate(pipeline):
        daily_diagnoses.append({"date": doc["_id"], "count": doc["count"]})

    # Top specialists platform-wide
    specialist_pipeline = [
        {"$unwind": "$selected_specialists"},
        {"$group": {"_id": "$selected_specialists", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_specialists = []
    async for doc in db.diagnoses.aggregate(specialist_pipeline):
        top_specialists.append({"specialist": doc["_id"], "count": doc["count"]})

    total_users = await db.users.count_documents({})
    total_diagnoses = await db.diagnoses.count_documents({})

    return {
        "total_users": total_users,
        "total_diagnoses": total_diagnoses,
        "daily_diagnoses_30d": daily_diagnoses,
        "top_specialists": top_specialists,
    }


@router.get("/time-series")
async def diagnosis_time_series(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
):
    """Get daily diagnosis counts for time-series chart (any authenticated user, scoped by role)."""
    db = get_database()
    is_admin = current_user.get("role") == "admin"

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    match_filter = {"created_at": {"$gte": cutoff}}
    if not is_admin:
        match_filter["user_id"] = current_user["_id"]

    pipeline = [
        {"$match": match_filter},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    results = {}
    async for doc in db.diagnoses.aggregate(pipeline):
        results[doc["_id"]] = doc["count"]

    # Fill gaps with zeros for a continuous series
    from datetime import date as date_type
    series = []
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        series.append({"date": d, "count": results.get(d, 0)})

    return {"days": days, "series": series}
