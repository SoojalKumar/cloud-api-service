"""Health service logic."""

from app.config import settings
from app.database import database_ready
from app.runtime import uptime_seconds


def get_health_payload() -> dict[str, object]:
    """Build the API health response."""

    db_status = "ok" if database_ready(settings.database_path) else "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": db_status,
        "uptime_seconds": round(uptime_seconds(), 3),
    }
