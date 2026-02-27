"""
Cura3.ai — Audit Logging Middleware
HIPAA-compliant audit trail for data access events.
Tracks: who accessed what resource, when, from where.
"""
import time
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Paths that contain PHI or sensitive data → always audit
AUDITED_PATH_PREFIXES = (
    "/api/v1/reports",
    "/api/v1/diagnosis",
    "/api/v1/chat",
    "/api/v1/admin",
    "/api/v1/users",
)

# Paths to skip (health checks, docs, static)
SKIP_PATHS = ("/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico")


def _extract_user_hint(request: Request) -> str:
    """Extract a user identifier hint from the Authorization header (without logging the full token)."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer ") and len(auth) > 20:
        # Store only a hash hint, NOT the full token (HIPAA)
        token_fragment = auth[-8:]
        return f"bearer_...{token_fragment}"
    return "anonymous"


def _get_client_ip(request: Request) -> str:
    """Get the originating client IP address."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that writes an audit log entry for every access
    to sensitive API endpoints. Stored in MongoDB `audit_logs` collection.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # Skip non-audited paths
        if path in SKIP_PATHS or not any(path.startswith(p) for p in AUDITED_PATH_PREFIXES):
            return await call_next(request)

        # Capture timing
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Build audit entry (NO PHI — only metadata)
        audit_entry = {
            "timestamp": datetime.now(timezone.utc),
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": _get_client_ip(request),
            "user_hint": _extract_user_hint(request),
            "user_agent": request.headers.get("user-agent", "unknown")[:200],
        }

        # Write asynchronously to MongoDB (fire-and-forget)
        try:
            from app.core.database import get_database
            db = get_database()
            if db is not None:
                # Don't await — fire and forget to avoid slowing the response
                import asyncio
                asyncio.create_task(db.audit_logs.insert_one(audit_entry))
        except Exception:
            # Never let audit logging break the app
            pass

        return response
