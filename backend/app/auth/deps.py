"""FastAPI dependencies for DB session, current user, and roles."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.service import require_roles, user_from_access_token
from app.core.config import Settings, get_settings
from app.core.enums import UserRole
from app.core.storage import Storage, get_storage
from app.database.session import get_db
from app.users.models import User

# Reads "Authorization: Bearer <access_token>"
bearer_scheme = HTTPBearer(auto_error=True)

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_file_storage() -> Storage:
    return get_storage()


FileStorage = Annotated[Storage, Depends(get_file_storage)]


def get_current_user(
    db: DbSession,
    settings: AppSettings,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> User:
    """Require a valid access token and return the user."""
    return user_from_access_token(db, credentials.credentials, settings)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole) -> Callable[..., User]:
    """Factory: dependency that allows only the given roles."""

    def _checker(user: CurrentUser) -> User:
        return require_roles(user, *roles)

    return _checker


RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
RequireEditorOrAdmin = Annotated[
    User, Depends(require_role(UserRole.ADMIN, UserRole.EDITOR))
]
