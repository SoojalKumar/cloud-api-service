"""FastAPI application entry point."""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.errors import (
    AppError,
    app_error_handler,
    http_error_handler,
    validation_error_handler,
)
from app.logging import configure_logging
from app.middleware.access_log import AccessLogMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routes.root import router as root_router
from app.routes.system import router as system_router
from app.routes.tasks import router as tasks_router


configure_logging()


def _frontend_dist_path() -> Optional[Path]:
    """Return the built frontend directory if it exists.

    Production deploys ship the React app as static files under
    ``frontend/dist`` (or ``FRONTEND_DIST_DIR``). When that directory is
    present we mount it at ``/`` so the demo lives on the same origin as
    the API; in development the JSON root endpoint stays in place so test
    runs and ad-hoc curl users keep getting the metadata response.
    """

    override = os.environ.get("FRONTEND_DIST_DIR")
    candidate = Path(override) if override else Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if (candidate / "index.html").is_file():
        return candidate
    return None


def create_app() -> FastAPI:
    """Build a fully wired FastAPI instance.

    Exposed as a factory so tests can re-build the app under different
    environments (e.g. with or without a built frontend on disk) without
    relying on import-time state.
    """

    instance = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A clean FastAPI foundation for a cloud-oriented backend service.",
    )
    instance.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    instance.add_middleware(SecurityHeadersMiddleware)
    instance.add_middleware(RequestIdMiddleware)
    instance.add_middleware(AccessLogMiddleware)
    instance.add_exception_handler(AppError, app_error_handler)
    instance.add_exception_handler(StarletteHTTPException, http_error_handler)
    instance.add_exception_handler(RequestValidationError, validation_error_handler)
    instance.include_router(system_router)
    instance.include_router(tasks_router)

    dist = _frontend_dist_path()
    if dist is not None:
        instance.mount(
            "/",
            StaticFiles(directory=dist, html=True),
            name="frontend",
        )
    else:
        instance.include_router(root_router)
    return instance


app = create_app()
