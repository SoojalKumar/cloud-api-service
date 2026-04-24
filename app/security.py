"""API authentication helpers."""

from typing import Optional

from fastapi import Header

from app.config import settings
from app.errors import AuthenticationError


API_KEY_HEADER = "X-API-Key"


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias=API_KEY_HEADER)) -> None:
    """Validate the shared API key used for protected endpoints."""

    if x_api_key != settings.api_key:
        raise AuthenticationError("Invalid API key.")
