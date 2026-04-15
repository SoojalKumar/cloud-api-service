"""Health and readiness routes."""

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health response for monitoring and smoke tests."""
    return {"status": "ok"}
