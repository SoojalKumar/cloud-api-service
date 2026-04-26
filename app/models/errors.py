"""Error response models for the API."""

from typing import Optional

from pydantic import BaseModel, Field


class ValidationFieldError(BaseModel):
    """Single field-level validation problem returned by the validation handler."""

    field: str = Field(..., examples=["body.title"])
    message: str = Field(..., examples=["Field required"])
    type: str = Field(..., examples=["missing"])


class ErrorResponse(BaseModel):
    """Standard API error payload returned by exception handlers."""

    error: str = Field(..., examples=["not_found"])
    message: str = Field(..., examples=["The requested resource was not found."])
    request_id: Optional[str] = Field(default=None, examples=["9f42dff9-4afd-4701"])
    fields: Optional[list[ValidationFieldError]] = Field(
        default=None,
        description="Populated for validation_error responses to point at the failing inputs.",
    )
