"""Simple in-process rate limiter middleware (IP + route bucket).

Uses settings for limits. Disabled when RATE_LIMIT_ENABLED=false (tests).
For multi-worker production, put a reverse-proxy limiter in front or switch
storage to Redis; this is assessment-ready and dependency-light.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _parse_limit(spec: str) -> tuple[int, int]:
    """Parse '10/minute' or '60/minute' → (max_requests, window_seconds)."""
    raw = (spec or "60/minute").strip().lower()
    count_s, _, unit = raw.partition("/")
    count = int(count_s)
    unit = unit.strip()
    if unit in {"second", "seconds", "sec", "s"}:
        window = 1
    elif unit in {"minute", "minutes", "min", "m"}:
        window = 60
    elif unit in {"hour", "hours", "h"}:
        window = 3600
    else:
        window = 60
    return count, window


def _bucket_for_path(path: str, api_prefix: str) -> str | None:
    """Return bucket name or None to skip limiting (health)."""
    prefix = api_prefix.rstrip("/")
    if path in {f"{prefix}/health", "/health"}:
        return None
    if path.endswith("/auth/login") or path.endswith("/auth/login/"):
        return "auth"
    if path.endswith("/auth/refresh") or path.endswith("/auth/refresh/"):
        return "auth"
    if f"{prefix}/passport/" in path or path.startswith(f"{prefix}/passport"):
        return "public"
    if path.startswith(prefix):
        return "api"
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)

        bucket = _bucket_for_path(request.url.path, settings.api_prefix)
        if bucket is None:
            return await call_next(request)

        if bucket == "auth":
            spec = settings.rate_limit_auth
        elif bucket == "public":
            spec = settings.rate_limit_public
        else:
            spec = settings.rate_limit_api

        max_requests, window = _parse_limit(spec)
        ip = _client_ip(request)
        key = f"{ip}:{bucket}"
        now = time.monotonic()

        with self._lock:
            q = self._hits[key]
            cutoff = now - window
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= max_requests:
                retry_after = max(1, int(window - (now - q[0])))
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                    headers={"Retry-After": str(retry_after)},
                )
            q.append(now)

        return await call_next(request)
