"""Health and readiness routes."""

from fastapi import APIRouter

from app.services.health import get_health_payload


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health response for monitoring and smoke tests."""
    return get_health_payload()
