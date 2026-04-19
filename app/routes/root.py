"""Root route for lightweight service discovery."""

from fastapi import APIRouter

from app.models.system import ServiceInfoResponse
from app.services.system import get_service_info_payload


router = APIRouter(tags=["root"])


@router.get("/", response_model=ServiceInfoResponse)
def root() -> ServiceInfoResponse:
    """Return basic service metadata from the API root."""

    return ServiceInfoResponse(**get_service_info_payload())
