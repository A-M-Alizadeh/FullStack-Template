"""Auth HTTP routes."""

from fastapi import APIRouter, status

from app.auth.deps import AppSettings, CurrentUser, DbSession
from app.auth.service import login, logout, refresh
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def auth_login(
    body: LoginRequest,
    db: DbSession,
    settings: AppSettings,
) -> TokenResponse:
    """Email + password → access + refresh tokens."""
    return login(
        db,
        email=body.email,
        password=body.password,
        settings=settings,
    )


@router.post("/refresh", response_model=TokenResponse)
def auth_refresh(
    body: RefreshRequest,
    db: DbSession,
    settings: AppSettings,
) -> TokenResponse:
    """Exchange a valid refresh token for a new pair (old refresh is revoked)."""
    return refresh(
        db,
        raw_refresh_token=body.refresh_token,
        settings=settings,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def auth_logout(body: LogoutRequest, db: DbSession) -> None:
    """Revoke the given refresh token."""
    logout(db, raw_refresh_token=body.refresh_token)


@router.get("/me", response_model=UserResponse)
def auth_me(user: CurrentUser) -> UserResponse:
    """Current user from the access token."""
    return UserResponse.model_validate(user)
