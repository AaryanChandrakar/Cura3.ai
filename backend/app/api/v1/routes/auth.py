"""
Cura3.ai — Authentication Routes
Google OAuth 2.0 flow + JWT token management.
Tokens are issued as httpOnly secure cookies for XSS protection.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from app.config import settings
from app.core.database import get_database
from app.core.security import create_access_token
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Cookie Configuration ─────────────────────────────────
IS_PRODUCTION = not settings.FRONTEND_URL.startswith("http://localhost")
COOKIE_NAME = "cura3_session"
COOKIE_MAX_AGE = settings.JWT_EXPIRATION_MINUTES * 60  # seconds

# ── Google OAuth Setup ───────────────────────────────────
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
async def login(request: Request):
    """Redirect user to Google OAuth consent screen."""
    redirect_uri = settings.OAUTH_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):
    """
    Handle Google OAuth callback.
    Creates user in DB if first login, then issues a JWT as an httpOnly cookie.
    Also passes a short-lived flag so the frontend knows auth succeeded.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {str(e)}",
        )

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user info from Google.",
        )

    db = get_database()

    # Check if user already exists
    existing_user = await db.users.find_one({"google_id": user_info["sub"]})

    if existing_user:
        # Update last login
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"updated_at": datetime.now(timezone.utc)}},
        )
        user_id = str(existing_user["_id"])
        role = existing_user.get("role", "patient")
    else:
        # Create new user
        new_user = {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "google_id": user_info["sub"],
            "avatar_url": user_info.get("picture"),
            "role": "patient",  # Default role
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(new_user)
        user_id = str(result.inserted_id)
        role = "patient"

    # Create JWT token
    jwt_token = create_access_token(
        data={"sub": user_id, "email": user_info.get("email"), "role": role}
    )

    # Redirect to frontend callback — token is sent BOTH ways:
    # 1. httpOnly cookie (secure, immune to XSS)
    # 2. URL param (for backward compat / localStorage fallback)
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
    response = RedirectResponse(url=frontend_url)
    response.set_cookie(
        key=COOKIE_NAME,
        value=jwt_token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,                     # Not accessible via JS
        secure=IS_PRODUCTION,              # HTTPS only in production
        samesite="lax",                    # CSRF protection
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    """Clear the httpOnly session cookie."""
    response = JSONResponse(content={"detail": "Logged out successfully."})
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
    )
    return response


@router.get("/me")
async def get_current_user_info(request: Request):
    """Get current authenticated user's info (requires Authorization header or cookie)."""
    from app.core.security import get_current_user
    from fastapi import Depends

    # This endpoint is better accessed via dependency injection.
    # See the /users/me endpoint in the main app.
    pass
