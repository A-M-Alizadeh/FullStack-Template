"""Unit tests for password hashing and JWT helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from app.auth.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.auth.service import require_roles
from app.core.config import get_settings
from app.core.enums import UserRole
from app.users.models import User


def test_hash_and_verify_password():
    """Hash verifies with the same password."""
    hashed = hash_password("secret-123")
    assert verify_password("secret-123", hashed)


def test_verify_password_wrong():
    """Wrong password does not verify."""
    hashed = hash_password("secret-123")
    assert not verify_password("other", hashed)


def test_access_token_roundtrip():
    """Access JWT encodes and decodes user id + role."""
    settings = get_settings()
    user_id = uuid4()
    token = create_access_token(user_id=user_id, role="admin", settings=settings)
    payload = decode_access_token(token, settings)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_decode_rejects_non_access_token():
    """Token without type=access is rejected."""
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "admin",
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token, settings)


def test_refresh_token_hash_is_stable():
    """Same raw refresh token always hashes the same."""
    raw = generate_refresh_token()
    assert hash_refresh_token(raw) == hash_refresh_token(raw)
    assert hash_refresh_token(raw) != hash_refresh_token(generate_refresh_token())


def test_require_roles_rejects_wrong_role():
    """Editor is rejected when only admin is allowed."""
    user = User(
        email="x@example.com",
        password_hash="x",
        role=UserRole.EDITOR,
    )
    with pytest.raises(Exception) as exc:
        require_roles(user, UserRole.ADMIN)
    assert exc.value.status_code == 403
