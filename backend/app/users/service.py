"""User admin CRUD."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.core.enums import UserRole
from app.products.models import Product
from app.schemas.auth import UserCreate, UserResponse, UserUpdate
from app.users.models import User


def list_users(db: Session) -> list[UserResponse]:
    rows = db.scalars(select(User).order_by(User.email)).all()
    return [UserResponse.model_validate(u) for u in rows]


def get_user(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _admin_count(db: Session) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
        )
        or 0
    )


def _ensure_not_last_admin(db: Session, user: User) -> None:
    if user.role == UserRole.ADMIN and _admin_count(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove or demote the last admin",
        )


def create_user(db: Session, body: UserCreate) -> UserResponse:
    user = User(
        email=str(body.email).lower(),
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    db.refresh(user)
    return UserResponse.model_validate(user)


def update_user(db: Session, user_id: UUID, body: UserUpdate) -> UserResponse:
    user = get_user(db, user_id)
    data = body.model_dump(exclude_unset=True)

    if "role" in data and data["role"] != user.role:
        if user.role == UserRole.ADMIN and data["role"] != UserRole.ADMIN:
            _ensure_not_last_admin(db, user)
        user.role = data["role"]

    if "email" in data and data["email"] is not None:
        user.email = str(data["email"]).lower()

    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    db.refresh(user)
    return UserResponse.model_validate(user)


def delete_user(db: Session, user_id: UUID, *, actor_id: UUID) -> None:
    if user_id == actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user = get_user(db, user_id)
    _ensure_not_last_admin(db, user)

    owns_product = db.scalar(
        select(Product.id).where(Product.created_by_id == user_id).limit(1)
    )
    if owns_product is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User owns products; reassign or delete them first",
        )

    db.delete(user)
    db.commit()
