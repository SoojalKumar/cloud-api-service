"""Logging configuration helpers."""

import logging

from app.config import settings


LOGGER_NAME = "cloud_api_service"


def configure_logging() -> None:
    """Configure application logging once for local and CI runs."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
