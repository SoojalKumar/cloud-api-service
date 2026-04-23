"""API authentication helpers."""

from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import settings


API_KEY_HEADER = "X-API-Key"


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias=API_KEY_HEADER)) -> None:
    """Validate the shared API key used for protected endpoints."""

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
