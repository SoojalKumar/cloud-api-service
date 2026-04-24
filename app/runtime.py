"""Runtime metadata shared across the application."""

from time import monotonic


# Captured when the module is first imported so it reflects process start.
_STARTED_AT = monotonic()


def uptime_seconds() -> float:
    """Return how long the current process has been running, in seconds."""

    return max(0.0, monotonic() - _STARTED_AT)
