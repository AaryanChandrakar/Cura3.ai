"""
Cura3.ai — Application Configuration
Centralized settings loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App ──────────────────────────────────────
    APP_NAME: str = "Cura3.ai"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── MongoDB Atlas ────────────────────────────
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "cura3ai"

    # ── OpenAI API ────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Google OAuth ─────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"

    # ── JWT / Auth ───────────────────────────────
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # ── CORS ─────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── File Upload ──────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".txt", ".pdf", ".docx"]

    # ── Monitoring (optional) ────────────────────
    APPINSIGHTS_CONNECTION_STRING: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
