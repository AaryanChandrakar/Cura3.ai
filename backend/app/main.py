"""
Cura3.ai — FastAPI Application Entry Point
Main application with CORS, lifecycle events, and route registration.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.core.security import get_current_user

# Import routes
from app.api.v1.routes import auth, reports, diagnosis, chat, admin, analytics


# ── Lifecycle Events ─────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await connect_to_mongodb()
    print(f"[APP] {settings.APP_NAME} v{settings.APP_VERSION} started.")
    yield
    # Shutdown
    await close_mongodb_connection()
    print(f"[APP] {settings.APP_NAME} shut down.")


# ── App Initialization ───────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered medical diagnostics platform with multi-specialist analysis.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────

# Session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (60 requests per minute per user/IP)
from app.core.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

# API usage tracking (analytics for admin)
from app.core.api_usage_tracker import APIUsageMiddleware
app.add_middleware(APIUsageMiddleware)

# Audit logging (HIPAA-compliant access trail)
from app.core.audit_logger import AuditLogMiddleware
app.add_middleware(AuditLogMiddleware)

# HTTPS enforcement (production only — when not running on localhost)
if not settings.FRONTEND_URL.startswith("http://localhost"):
    from app.core.https_redirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)



# ── Register API Routes ─────────────────────────────────

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(diagnosis.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)


# ── Root & Health Endpoints ──────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — health check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check for monitoring."""
    from app.core.database import get_database

    db = get_database()
    db_status = "connected" if db is not None else "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get(f"{settings.API_V1_PREFIX}/users/me", tags=["Users"])
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return {
        "id": current_user["_id"],
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "avatar_url": current_user.get("avatar_url"),
        "role": current_user.get("role", "patient"),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user.get("created_at"),
    }
