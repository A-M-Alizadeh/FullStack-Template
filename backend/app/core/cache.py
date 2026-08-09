"""Optional Redis cache with in-process no-op fallback."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any, Protocol

from app.core.config import Settings, get_settings

logger = logging.getLogger("app.cache")


class Cache(Protocol):
    def get_json(self, key: str) -> Any | None: ...

    def set_json(self, key: str, value: Any, *, ttl_seconds: int) -> None: ...

    def delete(self, *keys: str) -> None: ...


class NullCache:
    """Used when REDIS_URL is empty or Redis is unreachable."""

    def get_json(self, key: str) -> Any | None:
        return None

    def set_json(self, key: str, value: Any, *, ttl_seconds: int) -> None:
        return None

    def delete(self, *keys: str) -> None:
        return None


class RedisCache:
    def __init__(self, url: str) -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)

    def get_json(self, key: str) -> Any | None:
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: Any, *, ttl_seconds: int) -> None:
        self._client.set(key, json.dumps(value, default=str), ex=ttl_seconds)

    def delete(self, *keys: str) -> None:
        if keys:
            self._client.delete(*keys)


DASHBOARD_KEY = "dashboard:v1"
ANALYTICS_KEY = "analytics:v1"
DEFAULT_TTL = 30


def invalidate_stats_cache(cache: Cache | None = None) -> None:
    (cache or get_cache()).delete(DASHBOARD_KEY, ANALYTICS_KEY)


@lru_cache
def get_cache() -> Cache:
    settings = get_settings()
    url = (settings.redis_url or "").strip()
    if not url:
        return NullCache()
    try:
        cache = RedisCache(url)
        cache._client.ping()  # type: ignore[attr-defined]
        logger.info("redis cache enabled")
        return cache
    except Exception:
        logger.warning("redis unavailable; cache disabled", exc_info=True)
        return NullCache()


def reset_cache_for_tests() -> None:
    get_cache.cache_clear()
