"""Application-level exceptions and handlers."""

from typing import Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.errors import ErrorResponse


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


def _request_id(request: Request) -> Optional[str]:
    return getattr(request.state, "request_id", None)


def _json_error(
    request: Request,
    status_code: int,
    error: str,
    message: str,
) -> JSONResponse:
    payload = ErrorResponse(
        error=error,
        message=message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


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
    )
