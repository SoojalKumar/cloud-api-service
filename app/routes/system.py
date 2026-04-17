"""System and metadata routes."""

from fastapi import APIRouter

from app.models.system import HealthResponse, ServiceInfoResponse
from app.services.health import get_health_payload
from app.services.system import get_service_info_payload


router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return health metadata for monitoring and smoke tests."""

    return HealthResponse(**get_health_payload())


@router.get("/info", response_model=ServiceInfoResponse)
def service_info() -> ServiceInfoResponse:
    """Return public-facing service metadata."""

    return ServiceInfoResponse(**get_service_info_payload())
