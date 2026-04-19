"""Error response models for the API."""

from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard API error payload returned by exception handlers."""

    error: str = Field(..., examples=["not_found"])
    message: str = Field(..., examples=["The requested resource was not found."])
    request_id: Optional[str] = Field(default=None, examples=["9f42dff9-4afd-4701"])
