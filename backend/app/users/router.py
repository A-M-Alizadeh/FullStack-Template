"""Users admin CRUD (admin-only)."""

from uuid import UUID

from fastapi import APIRouter, status

from app.auth.deps import DbSession, RequireAdmin
from app.schemas.auth import UserCreate, UserResponse, UserUpdate
from app.users import service as users_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    db: DbSession,
    _: RequireAdmin,
) -> list[UserResponse]:
    return users_service.list_users(db)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    db: DbSession,
    _: RequireAdmin,
) -> UserResponse:
    return users_service.create_user(db, body)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: DbSession,
    _: RequireAdmin,
) -> UserResponse:
    return users_service.update_user(db, user_id, body)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: DbSession,
    actor: RequireAdmin,
) -> None:
    users_service.delete_user(db, user_id, actor_id=actor.id)
