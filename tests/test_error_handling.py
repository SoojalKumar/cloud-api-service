"""Tests for API error handling and request tracing."""

import logging

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.access_log import PROCESS_TIME_HEADER
from app.middleware.request_id import REQUEST_ID_HEADER


client = TestClient(app)


def test_missing_route_uses_standard_error_payload() -> None:
    response = client.get("/api/v1/missing", headers={REQUEST_ID_HEADER: "test-request-1"})

    assert response.status_code == 404
    assert response.headers[REQUEST_ID_HEADER] == "test-request-1"
    assert response.json() == {
        "error": "not_found",
        "message": "Not Found",
        "request_id": "test-request-1",
    }


def test_request_id_is_generated_when_missing() -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    assert response.headers[REQUEST_ID_HEADER]


def test_security_headers_are_added_to_responses() -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"


def test_csp_frame_ancestors_allows_approved_embedders() -> None:
    """The app is embedded by the Hugging Face Spaces catalog at
    ``huggingface.co/spaces/...``, so clickjacking protection needs to allow
    HF while rejecting arbitrary third-party framers. The modern ``frame-
    ancestors`` directive replaces ``X-Frame-Options: DENY`` so both
    constraints can coexist in one header."""

    response = client.get("/api/v1/info")

    assert response.status_code == 200
    csp = response.headers.get("Content-Security-Policy", "")
    assert "frame-ancestors" in csp
    assert "'self'" in csp
    assert "https://huggingface.co" in csp
    assert "https://*.hf.space" in csp
    # Legacy header is intentionally dropped so CSP is the single source of
    # truth for framing policy.
    assert "X-Frame-Options" not in response.headers


def test_process_time_header_is_added_to_responses() -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert PROCESS_TIME_HEADER in response.headers
    assert float(response.headers[PROCESS_TIME_HEADER]) >= 0


def test_access_log_includes_request_metadata(caplog) -> None:
    caplog.set_level(logging.INFO, logger="cloud_api_service.access")

    response = client.get("/api/v1/info", headers={REQUEST_ID_HEADER: "req-123"})

    assert response.status_code == 200
    assert "GET /api/v1/info -> 200 request_id=req-123" in caplog.text
