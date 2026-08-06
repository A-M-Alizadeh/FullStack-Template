"""Auth business logic: login, refresh, logout."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import RefreshToken
from app.auth.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_expiry,
    verify_password,
)
from app.core.config import Settings
from app.core.enums import UserRole
from app.schemas.auth import TokenResponse
from app.users.models import User

logger = logging.getLogger("app.auth")


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def _issue_tokens(db: Session, user: User, settings: Settings) -> TokenResponse:
    access = create_access_token(
        user_id=user.id,
        role=user.role.value,
        settings=settings,
    )
    raw_refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh),
            expires_at=refresh_expiry(settings),
        )
    )
    db.commit()
    return TokenResponse(access_token=access, refresh_token=raw_refresh)


def login(
    db: Session,
    *,
    email: str,
    password: str,
    settings: Settings,
) -> TokenResponse:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        logger.info("login failed email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    tokens = _issue_tokens(db, user, settings)
    logger.info("login ok user_id=%s role=%s", user.id, user.role.value)
    return tokens


def refresh(
    db: Session,
    *,
    raw_refresh_token: str,
    settings: Settings,
) -> TokenResponse:
    token_hash = hash_refresh_token(raw_refresh_token)
    row = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    now = datetime.now(UTC)

    if row is None or row.revoked_at is not None:
        logger.info("refresh failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < now:
        logger.info("refresh failed expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Rotate: old refresh becomes unusable.
    row.revoked_at = now
    user = get_user_by_id(db, row.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    tokens = _issue_tokens(db, user, settings)
    logger.info("refresh ok user_id=%s", user.id)
    return tokens


def logout(db: Session, *, raw_refresh_token: str) -> None:
    token_hash = hash_refresh_token(raw_refresh_token)
    row = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        db.commit()
        logger.info("logout user_id=%s", row.user_id)


def user_from_access_token(
    db: Session,
    token: str,
    settings: Settings,
) -> User:
    """Resolve Bearer access token to a User, or 401."""
    try:
        payload = decode_access_token(token, settings)
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(user: User, *roles: UserRole) -> User:
    if user.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
