"""Application-level exceptions and handlers."""

from typing import Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.errors import ErrorResponse, ValidationFieldError


class AppError(Exception):
    """Base exception for expected application failures."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = "application_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AppError):
    """Raised when a requested resource cannot be found."""

    status_code = status.HTTP_404_NOT_FOUND
    error = "not_found"


class AuthenticationError(AppError):
    """Raised when request authentication fails."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error = "unauthorized"


def _request_id(request: Request) -> Optional[str]:
    return getattr(request.state, "request_id", None)


def _json_error(
    request: Request,
    status_code: int,
    error: str,
    message: str,
    fields: Optional[list[ValidationFieldError]] = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=error,
        message=message,
        request_id=_request_id(request),
        fields=fields,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle expected application errors with a consistent payload."""

    return _json_error(request, exc.status_code, exc.error, exc.message)


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Normalize FastAPI and Starlette HTTP errors."""

    error = "not_found" if exc.status_code == status.HTTP_404_NOT_FOUND else "http_error"
    return _json_error(request, exc.status_code, error, str(exc.detail))


def _format_validation_fields(exc: RequestValidationError) -> list[ValidationFieldError]:
    """Project Pydantic's structured errors into a stable, client-safe shape.

    We deliberately omit ``ctx`` and ``input`` from Pydantic's raw error dicts
    because those can echo user input back into the response and inflate the
    payload; ``loc``, ``msg``, and ``type`` are enough to point the caller at
    the failing field.
    """

    fields: list[ValidationFieldError] = []
    for err in exc.errors():
        loc = err.get("loc") or ()
        field = ".".join(str(part) for part in loc) or "request"
        fields.append(
            ValidationFieldError(
                field=field,
                message=str(err.get("msg", "Invalid value")),
                type=str(err.get("type", "value_error")),
            )
        )
    return fields


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Normalize request validation errors."""

    return _json_error(
        request,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "validation_error",
        "Request validation failed.",
        fields=_format_validation_fields(exc),
    )
