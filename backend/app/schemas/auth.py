"""Auth request/response shapes (HTTP boundary only)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    """Optional body fallback; browsers use the httpOnly cookie."""

    refresh_token: str | None = None


class LogoutRequest(BaseModel):
    """Optional body fallback; browsers use the httpOnly cookie."""

    refresh_token: str | None = None


class AccessTokenResponse(BaseModel):
    """Access JWT only — refresh is httpOnly cookie, not in JSON."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user fields — never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime
