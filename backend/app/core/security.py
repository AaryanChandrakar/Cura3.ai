"""
Cura3.ai — Security Utilities
JWT token handling, password-less Google OAuth, and role-based access control.
Supports dual-mode auth: Bearer header OR httpOnly cookie.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.core.database import get_database

# auto_error=False so we can fall back to cookie-based auth
security_scheme = HTTPBearer(auto_error=False)

COOKIE_NAME = "cura3_session"


# ── JWT Token Management ─────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Current User Dependency ──────────────────────────────

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
):
    """
    FastAPI dependency: extract and validate the current user from JWT.
    Checks Authorization header first, then falls back to httpOnly cookie.
    """
    token: Optional[str] = None

    # Priority 1: Bearer token from Authorization header
    if credentials:
        token = credentials.credentials

    # Priority 2: httpOnly cookie
    if not token:
        token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token or sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    db = get_database()
    from bson import ObjectId

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user["_id"] = str(user["_id"])
    return user


# ── Role-Based Access Control ────────────────────────────

def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory: restrict access to specific roles.
    Usage: Depends(require_role("admin", "doctor"))
    """

    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# ── HIPAA-Aware Helpers ──────────────────────────────────

def sanitize_log_data(data: dict) -> dict:
    """
    Remove PHI (Protected Health Information) from data before logging.
    Keeps only safe metadata fields.
    """
    safe_fields = {"_id", "user_id", "created_at", "updated_at", "role", "status"}
    return {k: v for k, v in data.items() if k in safe_fields}
