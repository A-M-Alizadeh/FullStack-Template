"""Auth API: login, refresh, logout, me."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.users.models import User


def test_login_ok(client: TestClient, admin_user: User):
    """Valid credentials return access and refresh tokens."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "admin-pass"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_bad_password(client: TestClient, admin_user: User):
    """Wrong password returns 401."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "nope"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password"


def test_login_unknown_email(client: TestClient):
    """Unknown email returns the same 401 as a bad password."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "x"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password"


def test_me_ok(client: TestClient, admin_user: User, admin_headers: dict[str, str]):
    """Bearer access token returns the current user."""
    r = client.get("/api/v1/auth/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["email"] == admin_user.email


def test_me_missing_token(client: TestClient):
    """No Authorization header returns 401/403 from the bearer scheme."""
    r = client.get("/api/v1/auth/me")
    assert r.status_code in (401, 403)


def test_me_garbage_token(client: TestClient):
    """Malformed Bearer token returns 401."""
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert r.status_code == 401


def test_me_expired_token(client: TestClient, admin_user: User):
    """Expired access token returns 401."""
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": str(admin_user.id),
            "role": "admin",
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


def test_refresh_ok(client: TestClient, admin_user: User):
    """Refresh returns a new token pair and rotates the refresh token."""
    login = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "admin-pass"},
    ).json()
    r = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login["refresh_token"]},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["refresh_token"] != login["refresh_token"]


def test_refresh_after_logout(client: TestClient, admin_user: User):
    """Refresh token cannot be used after logout."""
    login = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "admin-pass"},
    ).json()
    out = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": login["refresh_token"]},
    )
    assert out.status_code == 204
    r = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login["refresh_token"]},
    )
    assert r.status_code == 401


def test_refresh_unknown_token(client: TestClient):
    """Unknown refresh token returns 401."""
    r = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "totally-fake"},
    )
    assert r.status_code == 401


def test_me_unknown_user_id_in_token(client: TestClient):
    """Valid JWT for a deleted/missing user returns 401."""
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "admin",
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401
