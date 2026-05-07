"""Application configuration using Pydantic Settings."""

import os
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AdeshX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./adeshx.db"

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "mistral-saba-24b"

    # File Storage
    UPLOAD_DIR: str = "uploads"

    # Demo mode (works without API key)
    DEMO_MODE: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["https://adesh-x.vercel.app"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def upload_path(self) -> Path:
        """Get absolute upload directory path."""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_ai_available(self) -> bool:
        """Check if AI services are available."""
        return bool(self.GROQ_API_KEY) and not self.DEMO_MODE


settings = Settings()
