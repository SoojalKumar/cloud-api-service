"""Application configuration helpers."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOTENV_PATH = PROJECT_ROOT / ".env"
ALLOWED_ENVIRONMENTS = {"development", "test", "staging", "production"}
ALLOWED_LOG_LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}


def _clean_env_value(value: str) -> str:
    """Normalize .env values by trimming whitespace and wrapping quotes."""

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _load_dotenv(path: Path = DEFAULT_DOTENV_PATH) -> None:
    """Load simple KEY=VALUE pairs from a local .env file if present."""

    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), _clean_env_value(value))



def _csv_env(name: str, default: str = "") -> list[str]:
    """Parse a comma-separated environment variable into clean values."""

    raw_value = os.getenv(name, default)
    return [value.strip() for value in raw_value.split(",") if value.strip()]



def _validated_choice(name: str, value: str, allowed: Iterable[str]) -> str:
    """Validate that a config value belongs to an allowed set."""

    normalized = value.strip()
    allowed_values = set(allowed)
    if normalized not in allowed_values:
        formatted = ", ".join(sorted(allowed_values))
        raise ValueError(f"{name} must be one of: {formatted}.")
    return normalized



def _validated_log_level(value: str) -> str:
    """Normalize and validate log level configuration."""

    return _validated_choice("LOG_LEVEL", value.upper(), ALLOWED_LOG_LEVELS)



def _non_empty_env(name: str, default: Optional[str] = None) -> str:
    """Return a non-empty environment value or a default."""

    raw_value = os.getenv(name, default if default is not None else "")
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{name} must not be empty.")
    return value


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = field(default_factory=lambda: _non_empty_env("APP_NAME", "Cloud-Based API Service"))
    app_version: str = field(default_factory=lambda: _non_empty_env("APP_VERSION", "0.1.0"))
    environment: str = field(
        default_factory=lambda: _validated_choice(
            "APP_ENV",
            _non_empty_env("APP_ENV", "development"),
            ALLOWED_ENVIRONMENTS,
        )
    )
    database_path: str = field(default_factory=lambda: _non_empty_env("DATABASE_PATH", "cloud_api_service.db"))
    api_key: str = field(default_factory=lambda: _non_empty_env("API_KEY", "development-api-key"))
    log_level: str = field(default_factory=lambda: _validated_log_level(os.getenv("LOG_LEVEL", "INFO")))
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: _csv_env("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    )


settings = Settings()
