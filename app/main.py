"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.routes.system import router as system_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A clean FastAPI foundation for a cloud-oriented backend service.",
)

app.include_router(system_router)
