"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.errors import (
    AppError,
    app_error_handler,
    http_error_handler,
    validation_error_handler,
)
from app.middleware.request_id import RequestIdMiddleware
from app.routes.root import router as root_router
from app.routes.system import router as system_router
from app.routes.tasks import router as tasks_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A clean FastAPI foundation for a cloud-oriented backend service.",
)

app.add_middleware(RequestIdMiddleware)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(root_router)
app.include_router(system_router)
app.include_router(tasks_router)
