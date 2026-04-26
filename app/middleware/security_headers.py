"""Security header middleware for API responses."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Baseline headers that apply to every response regardless of origin.
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# Clickjacking protection. We deliberately use the modern `Content-Security-
# Policy: frame-ancestors` directive instead of `X-Frame-Options: DENY` so the
# live demo can be embedded inside the Hugging Face Spaces catalog page (which
# iframes the `*.hf.space` subdomain from `huggingface.co`). CSP
# `frame-ancestors` supersedes `X-Frame-Options` in every modern browser, so a
# single header both restricts embedding to approved origins and stays
# compatible with the deploy target. Change this list if the app is hosted
# behind a different embedder.
FRAME_ANCESTORS = (
    "'self'",
    "https://huggingface.co",
    "https://*.huggingface.co",
    "https://*.hf.space",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach baseline browser security headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        response.headers.setdefault(
            "Content-Security-Policy",
            f"frame-ancestors {' '.join(FRAME_ANCESTORS)}",
        )
        return response
