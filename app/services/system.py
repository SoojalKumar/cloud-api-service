"""System metadata service logic."""

from app.config import settings


def get_service_info_payload() -> dict[str, str]:
    """Build the public service metadata response."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs",
        "auth_mode": "api_key",
        "persistence": "sqlite",
    }
