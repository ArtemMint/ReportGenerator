"""
Application configuration settings using Pydantic's BaseSettings.
This class loads settings from environment variables and .env files, providing a centralized place for
all configuration values used across the application.
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App 2026"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()