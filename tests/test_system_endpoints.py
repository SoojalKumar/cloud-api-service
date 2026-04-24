"""Tests for system-level API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_service_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    uptime = payload.pop("uptime_seconds")
    assert payload == {
        "status": "ok",
        "service": "Cloud-Based API Service",
        "version": "0.1.0",
        "environment": "development",
        "database": "ok",
    }
    assert isinstance(uptime, (int, float))
    assert uptime >= 0


def test_info_endpoint_returns_public_metadata() -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Cloud-Based API Service",
        "version": "0.1.0",
        "environment": "development",
        "docs_url": "/docs",
        "auth_mode": "api_key",
        "persistence": "sqlite",
    }
