"""Application configuration helpers."""

from dataclasses import dataclass, field
import os


def _csv_env(name: str, default: str = "") -> list[str]:
    """Parse a comma-separated environment variable into clean values."""

    raw_value = os.getenv(name, default)
    return [value.strip() for value in raw_value.split(",") if value.strip()]


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "Cloud-Based API Service")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("APP_ENV", "development")
    database_path: str = os.getenv("DATABASE_PATH", "cloud_api_service.db")
    api_key: str = os.getenv("API_KEY", "development-api-key")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: _csv_env("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    )


settings = Settings()
