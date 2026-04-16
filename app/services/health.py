"""Health service logic."""

from app.config import settings


def get_health_payload() -> dict[str, str]:
    """Build the API health response."""

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
