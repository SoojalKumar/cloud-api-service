"""Tests for the root path under both dev and frontend-deployed modes."""

from pathlib import Path
from typing import Optional

from fastapi.testclient import TestClient

from app.main import create_app


def _build_app_with_frontend_dir(monkeypatch, dist_dir: Optional[Path]) -> TestClient:
    if dist_dir is None:
        monkeypatch.setenv("FRONTEND_DIST_DIR", "/nonexistent/frontend/dist")
    else:
        monkeypatch.setenv("FRONTEND_DIST_DIR", str(dist_dir))
    return TestClient(create_app())


def test_root_returns_service_metadata_when_no_frontend_is_built(monkeypatch) -> None:
    client = _build_app_with_frontend_dir(monkeypatch, dist_dir=None)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Cloud-Based API Service",
        "version": "0.1.0",
        "environment": "development",
        "docs_url": "/docs",
        "auth_mode": "api_key",
        "persistence": "sqlite",
    }


def test_root_serves_built_frontend_when_dist_is_present(monkeypatch, tmp_path) -> None:
    """When ``frontend/dist`` exists, ``/`` should serve ``index.html`` so the
    demo UI is reachable on the same origin as the API."""

    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>Demo</title>")

    client = _build_app_with_frontend_dir(monkeypatch, dist_dir=dist)

    response = client.get("/")

    assert response.status_code == 200
    assert "<!doctype html>" in response.text.lower()
    assert "demo" in response.text.lower()
    # API surface is unaffected by mounting the static site at root.
    api_response = client.get("/api/v1/info")
    assert api_response.status_code == 200
    assert api_response.json()["name"] == "Cloud-Based API Service"
