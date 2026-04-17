"""Response models for system-level endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health status payload for monitoring and readiness checks."""

    status: str
    service: str
    version: str
    environment: str


class ServiceInfoResponse(BaseModel):
    """Basic service metadata exposed to clients."""

    name: str
    version: str
    environment: str
    docs_url: str
