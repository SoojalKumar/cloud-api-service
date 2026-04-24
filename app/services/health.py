"""Health service logic."""

from app.config import settings
from app.database import database_ready


def get_health_payload() -> dict[str, str]:
    """Build the API health response."""

    db_status = "ok" if database_ready(settings.database_path) else "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": db_status,
    }
