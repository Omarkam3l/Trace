"""Rate limiting middleware for FastAPI."""

from __future__ import annotations

import threading
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-user sliding-window rate limiting middleware."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60) -> None:
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}
        self._lock = threading.RLock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        user = getattr(request.state, "user", None)
        user_id = user.user_id if user else request.client.host if request.client else "anonymous"

        now = time.time()
        cutoff = now - self._window_seconds

        with self._lock:
            timestamps = self._buckets.get(user_id, [])
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= self._max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"error": {"type": "RateLimitExceededError", "message": "Rate limit exceeded"}},
                )

            timestamps.append(now)
            self._buckets[user_id] = timestamps

        return await call_next(request)
