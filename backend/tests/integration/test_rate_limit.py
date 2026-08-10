"""Rate limiting middleware."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.rate_limit import _bucket_for_path, _parse_limit
from app.users.models import User


def test_parse_limit_units():
    assert _parse_limit("10/minute") == (10, 60)
    assert _parse_limit("5/hour") == (5, 3600)


def test_bucket_mapping():
    assert _bucket_for_path("/api/v1/health", "/api/v1") is None
    assert _bucket_for_path("/api/v1/auth/login", "/api/v1") == "auth"
    assert _bucket_for_path("/api/v1/passport/abc", "/api/v1") == "public"
    assert _bucket_for_path("/api/v1/products", "/api/v1") == "api"


def test_login_rate_limited(client: TestClient, admin_user: User, monkeypatch):
    """Auth bucket returns 429 after the configured limit."""
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_AUTH", "3/minute")
    get_settings.cache_clear()

    codes = [
        client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "wrong"},
        ).status_code
        for _ in range(5)
    ]

    assert codes[:3] == [401, 401, 401]
    assert codes[3:] == [429, 429]
    assert "Retry-After" in client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrong"},
    ).headers

    get_settings.cache_clear()
