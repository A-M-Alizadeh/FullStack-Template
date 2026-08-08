"""httpOnly refresh-token cookie helpers."""

from __future__ import annotations

from fastapi import Response

from app.core.config import Settings

REFRESH_COOKIE = "refresh_token"


def refresh_cookie_path(settings: Settings) -> str:
    return f"{settings.api_prefix.rstrip('/')}/auth"


def set_refresh_cookie(response: Response, raw_token: str, settings: Settings) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=raw_token,
        max_age=settings.refresh_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=refresh_cookie_path(settings),
    )


def clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE,
        path=refresh_cookie_path(settings),
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
