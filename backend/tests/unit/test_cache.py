"""Unit tests for cache helpers."""

from app.core.cache import NullCache, invalidate_stats_cache


def test_null_cache_is_noop():
    cache = NullCache()
    assert cache.get_json("dashboard:v1") is None
    cache.set_json("dashboard:v1", {"ok": True}, ttl_seconds=10)
    assert cache.get_json("dashboard:v1") is None
    invalidate_stats_cache(cache)
