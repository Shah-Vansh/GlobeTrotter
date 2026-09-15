"""
Simple sliding-window rate limiter (per client IP).

Protects /api/chat from accidental floods. Not a substitute for a reverse
proxy limit in true production, but sufficient for single-node deploy.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable, Deque

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# path prefixes that are rate-limited
LIMITED_PREFIXES = ("/api/chat",)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if not any(path.startswith(p) for p in LIMITED_PREFIXES):
            return await call_next(request)

        settings = get_settings()
        limit = settings.rate_limit_requests
        window = settings.rate_limit_window_seconds

        if limit <= 0:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        q = self._hits[client]

        # drop timestamps outside the window
        while q and now - q[0] > window:
            q.popleft()

        if len(q) >= limit:
            logger.warning(
                "RATE_LIMITED client=%s path=%s count=%d window=%ds",
                client,
                path,
                len(q),
                window,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Too many requests. Please wait a moment and try again.",
                    "retry_after_seconds": window,
                },
                headers={"Retry-After": str(window)},
            )

        q.append(now)
        return await call_next(request)
