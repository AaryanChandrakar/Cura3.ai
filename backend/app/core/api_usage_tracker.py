"""
Cura3.ai — API Usage Tracking Middleware
Tracks request counts per endpoint for API usage monitoring.
Data stored in MongoDB `api_usage` collection.
"""
import re
import time
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Paths to skip tracking
SKIP_PATHS = ("/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico")

# Regex to normalize MongoDB ObjectIDs in paths
_OBJECTID_RE = re.compile(r"/[a-f0-9]{24}")


class APIUsageMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks API usage statistics:
    - Request count per endpoint (hourly buckets)
    - Response times
    - Status code distribution
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # Skip non-API paths
        if path in SKIP_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Normalize path (replace ObjectIDs with {id} for aggregation)
        normalized_path = _OBJECTID_RE.sub("/{id}", path)
        endpoint_key = f"{method} {normalized_path}"

        # Hourly bucket
        now = datetime.now(timezone.utc)
        hour_bucket = now.replace(minute=0, second=0, microsecond=0)

        # Fire-and-forget write to MongoDB
        try:
            from app.core.database import get_database
            db = get_database()
            if db is not None:
                import asyncio
                asyncio.create_task(
                    self._record_usage(db, endpoint_key, hour_bucket, duration_ms, response.status_code, now)
                )
        except Exception:
            pass

        return response

    @staticmethod
    async def _record_usage(db, endpoint: str, hour_bucket, duration_ms: float, status_code: int, now):
        """Record a single API usage event in MongoDB."""
        try:
            status_key = f"status_codes.s{status_code}"
            await db.api_usage.update_one(
                {
                    "endpoint": endpoint,
                    "hour_bucket": hour_bucket,
                },
                {
                    "$inc": {
                        "request_count": 1,
                        status_key: 1,
                        "total_duration_ms": duration_ms,
                    },
                    "$min": {"min_duration_ms": duration_ms},
                    "$max": {"max_duration_ms": duration_ms},
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
            )
        except Exception:
            pass
