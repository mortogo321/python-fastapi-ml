import time
from collections import defaultdict
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter middleware.

    Tracks requests per client IP within a sliding time window.
    Returns HTTP 429 Too Many Requests when the limit is exceeded.
    Health endpoints are exempt so orchestrators never get throttled.
    """

    EXEMPT_PATHS = {"/api/health", "/api/v1/health", "/api/v1/health/ollama", "/"}

    def __init__(self, app: Any, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self._clients: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()[:45]
        return request.client.host if request.client else "unknown"

    def _cleanup_window(self, timestamps: list[float], now: float) -> list[float]:
        cutoff = now - self.window_seconds
        return [ts for ts in timestamps if ts > cutoff]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        self._clients[client_ip] = self._cleanup_window(self._clients[client_ip], now)

        if len(self._clients[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after_seconds": self.window_seconds,
                },
            )

        self._clients[client_ip].append(now)
        return await call_next(request)
