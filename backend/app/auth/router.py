"""Auth HTTP routes."""

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.auth.cookies import (
    REFRESH_COOKIE,
    clear_refresh_cookie,
    set_refresh_cookie,
)
from app.auth.deps import AppSettings, CurrentUser, DbSession
from app.auth.service import login, logout, refresh
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _refresh_from_request(
    request: Request, body_token: str | None
) -> str | None:
    """Prefer httpOnly cookie; optional JSON body for tests / non-browser clients."""
    return request.cookies.get(REFRESH_COOKIE) or body_token


@router.post("/login", response_model=AccessTokenResponse)
def auth_login(
    body: LoginRequest,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> AccessTokenResponse:
    """Email + password → access JWT + httpOnly refresh cookie."""
    tokens = login(
        db,
        email=body.email,
        password=body.password,
        settings=settings,
    )
    set_refresh_cookie(response, tokens.refresh_token, settings)
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def auth_refresh(
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
    body: RefreshRequest | None = None,
) -> AccessTokenResponse:
    """Rotate refresh (cookie or body) and return a new access token."""
    raw = _refresh_from_request(
        request, body.refresh_token if body is not None else None
    )
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    tokens = refresh(db, raw_refresh_token=raw, settings=settings)
    set_refresh_cookie(response, tokens.refresh_token, settings)
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def auth_logout(
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
    body: LogoutRequest | None = None,
) -> None:
    """Revoke refresh token and clear the cookie."""
    raw = _refresh_from_request(
        request, body.refresh_token if body is not None else None
    )
    if raw:
        logout(db, raw_refresh_token=raw)
    clear_refresh_cookie(response, settings)


@router.get("/me", response_model=UserResponse)
def auth_me(user: CurrentUser) -> UserResponse:
    """Current user from the access token."""
    return UserResponse.model_validate(user)
