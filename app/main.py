"""FastAPI application entry point."""

from fastapi import FastAPI

from app.routes.health import router as health_router


app = FastAPI(
    title="Cloud-Based API Service",
    version="0.1.0",
    description="A clean FastAPI foundation for a cloud-oriented backend service.",
)

app.include_router(health_router)
