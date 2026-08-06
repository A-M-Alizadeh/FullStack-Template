"""Seed admin and editor users for local development.

Usage (from backend/):
  APP_ENV=local uv run python -m scripts.seed_users
"""

from __future__ import annotations

import logging

from sqlalchemy import select

import app.database.load_models  # noqa: F401
from app.auth.security import hash_password
from app.core.enums import UserRole
from app.database.session import SessionLocal
from app.users.models import User

logger = logging.getLogger("app.seed")

# Dev-only defaults. Change after first login in real deployments.
SEED_USERS = (
    {
        "email": "admin@example.com",
        "password": "admin1234",
        "role": UserRole.ADMIN,
    },
    {
        "email": "editor@example.com",
        "password": "editor1234",
        "role": UserRole.EDITOR,
    },
    {
        "email": "aliadmin@example.com",
        "password": "123456789",
        "role": UserRole.ADMIN,
    },
    {
        "email": "alieditor@example.com",
        "password": "123456789",
        "role": UserRole.EDITOR,
    },
)


def seed_users() -> None:
    db = SessionLocal()
    try:
        for item in SEED_USERS:
            exists = db.scalar(select(User).where(User.email == item["email"]))
            if exists is not None:
                logger.info("skip existing %s", item["email"])
                continue
            db.add(
                User(
                    email=item["email"],
                    password_hash=hash_password(item["password"]),
                    role=item["role"],
                )
            )
            logger.info("created %s (%s)", item["email"], item["role"].value)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_users()
    print("seed done")
