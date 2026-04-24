"""Access logging middleware with request timing."""

import logging
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


PROCESS_TIME_HEADER = "X-Process-Time"
logger = logging.getLogger("cloud_api_service.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Log request/response metadata and expose process timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = perf_counter()
        response = await call_next(request)
        duration_seconds = perf_counter() - start
        response.headers[PROCESS_TIME_HEADER] = f"{duration_seconds:.6f}"
        logger.info(
            "%s %s -> %s request_id=%s duration=%.6fs",
            request.method,
            request.url.path,
            response.status_code,
            getattr(request.state, "request_id", "missing"),
            duration_seconds,
        )
        return response
