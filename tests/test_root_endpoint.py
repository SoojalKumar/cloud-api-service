"""Tests for the API root endpoint."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Cloud-Based API Service",
        "version": "0.1.0",
        "environment": "development",
        "docs_url": "/docs",
    }
