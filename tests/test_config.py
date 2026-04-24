"""Tests for runtime configuration helpers."""

from pathlib import Path

import pytest

from app.config import _csv_env, _load_dotenv, _validated_choice, _validated_log_level


def test_csv_env_ignores_empty_values(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000, https://example.com, ,",
    )

    assert _csv_env("CORS_ALLOWED_ORIGINS") == [
        "http://localhost:3000",
        "https://example.com",
    ]


def test_load_dotenv_sets_missing_environment_values(tmp_path, monkeypatch) -> None:
    dotenv_path = Path(tmp_path / ".env")
    dotenv_path.write_text('API_KEY="from-dotenv"\nAPP_ENV=staging\n')
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    _load_dotenv(dotenv_path)

    assert _csv_env("API_KEY") == ["from-dotenv"]
    assert _csv_env("APP_ENV") == ["staging"]


def test_load_dotenv_does_not_override_existing_values(tmp_path, monkeypatch) -> None:
    dotenv_path = Path(tmp_path / ".env")
    dotenv_path.write_text('API_KEY="from-dotenv"\n')
    monkeypatch.setenv("API_KEY", "from-environment")

    _load_dotenv(dotenv_path)

    assert _csv_env("API_KEY") == ["from-environment"]


def test_validated_choice_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        _validated_choice("APP_ENV", "invalid", {"development", "production"})


def test_validated_log_level_normalizes_value() -> None:
    assert _validated_log_level("debug") == "DEBUG"
