"""Shared fixtures for unit and integration tests.

Integration tests use a separate Postgres DB: dpp_test.
Requires: docker compose up db
"""

from __future__ import annotations

import os
from collections.abc import Generator
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Must be set before app settings / engine are loaded.
os.environ["APP_ENV"] = "local"
os.environ["POSTGRES_DB"] = "dpp_test"

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()
settings = get_settings()


def _ensure_test_database() -> None:
    admin = create_engine(
        (
            f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/postgres"
        ),
        isolation_level="AUTOCOMMIT",
    )
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": settings.postgres_db},
        ).scalar()
        if exists is None:
            conn.execute(text(f'CREATE DATABASE "{settings.postgres_db}"'))
    admin.dispose()


_ensure_test_database()

import app.database.load_models  # noqa: E402, F401
from app.auth.deps import get_file_storage  # noqa: E402
from app.auth.security import hash_password  # noqa: E402
from app.core.enums import UserRole  # noqa: E402
from app.core.storage import LocalStorage  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.session import engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.products.models import CertificationType, IssuingAuthority  # noqa: E402
from app.users.models import User  # noqa: E402

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# Recreate schema each session so model changes (e.g. new columns) apply to dpp_test.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_db() -> Generator[None, None, None]:
    """Empty tables before each test so runs stay isolated."""
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def storage(tmp_path: Path) -> LocalStorage:
    return LocalStorage(root=tmp_path / "uploads")


@pytest.fixture
def client(db: Session, storage: LocalStorage) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        yield db

    def override_storage() -> LocalStorage:
        return storage

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_file_storage] = override_storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def parallel_client(
    storage: LocalStorage,
) -> Generator[TestClient, None, None]:
    """Client with a fresh DB session per request (needed for concurrency)."""

    def override_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def override_storage() -> LocalStorage:
        return storage

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_file_storage] = override_storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db: Session) -> User:
    user = User(
        email="admin@example.com",
        password_hash=hash_password("admin-pass"),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def editor_user(db: Session) -> User:
    user = User(
        email="editor@example.com",
        password_hash=hash_password("editor-pass"),
        role=UserRole.EDITOR,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "admin-pass"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def editor_headers(client: TestClient, editor_user: User) -> dict[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        json={"email": editor_user.email, "password": "editor-pass"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def lookups(db: Session) -> dict[str, str]:
    """Minimal cert type + authority for certification tests."""
    cert_type = CertificationType(code="ce", name="CE Marking")
    authority = IssuingAuthority(code="tuv", name="TÜV")
    db.add_all([cert_type, authority])
    db.commit()
    db.refresh(cert_type)
    db.refresh(authority)
    return {
        "certification_type_id": str(cert_type.id),
        "issuing_authority_id": str(authority.id),
    }


def product_body(**overrides: object) -> dict:
    body: dict = {
        "name": "Test Product",
        "sku": f"SKU-{uuid4().hex[:8]}",
        "serial_number": f"SN-{uuid4().hex[:8]}",
        "category": "electronics",
        "description": "test",
        "production_date": date(2024, 1, 15).isoformat(),
        "country_of_origin": "DE",
    }
    body.update(overrides)
    return body
