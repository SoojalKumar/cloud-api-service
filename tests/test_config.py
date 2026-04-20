"""Tests for runtime configuration helpers."""

from app.config import _csv_env


def test_csv_env_ignores_empty_values(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000, https://example.com, ,",
    )

    assert _csv_env("CORS_ALLOWED_ORIGINS") == [
        "http://localhost:3000",
        "https://example.com",
    ]
