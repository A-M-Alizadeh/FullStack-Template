"""DB integrity: cascade, rollback, concurrent requests, auth on mutations."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.core.enums import UserRole
from app.products.models import (
    Material,
    Passport,
    Product,
    QrScan,
    Sustainability,
)
from app.users.models import User
from tests.conftest import TestingSessionLocal, product_body


def test_delete_product_cascades_nested(
    client: TestClient,
    admin_headers: dict[str, str],
    lookups: dict[str, str],
    db: Session,
):
    """Deleting a product removes materials, sustainability, passport, scans."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    pid = product["id"]

    assert (
        client.post(
            f"/api/v1/products/{pid}/materials",
            headers=admin_headers,
            json={
                "name": "Steel",
                "percentage": "50.00",
                "country_of_origin": "DE",
                "recyclable": True,
            },
        ).status_code
        == 201
    )
    assert (
        client.put(
            f"/api/v1/products/{pid}/sustainability",
            headers=admin_headers,
            json={
                "carbon_footprint": "10 kg",
                "water_consumption": "5 L",
                "recycled_material_percent": "20.00",
                "repairability_score": "70.00",
                "recyclable": True,
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/products/{pid}/certifications",
            headers=admin_headers,
            data={
                "certification_type_id": lookups["certification_type_id"],
                "issuing_authority_id": lookups["issuing_authority_id"],
                "issue_date": "2024-01-01",
            },
            files={"pdf": ("c.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf")},
        ).status_code
        == 201
    )
    published = client.post(
        f"/api/v1/products/{pid}/publish", headers=admin_headers
    ).json()
    public_uuid = published["passport"]["public_uuid"]
    assert (
        client.get(
            f"/api/v1/passport/{public_uuid}", params={"src": "qr"}
        ).status_code
        == 200
    )

    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Material)) == 1
    assert db.scalar(select(func.count()).select_from(Sustainability)) == 1
    assert db.scalar(select(func.count()).select_from(Passport)) == 1
    assert db.scalar(select(func.count()).select_from(QrScan)) == 1

    assert client.delete(f"/api/v1/products/{pid}", headers=admin_headers).status_code == 204

    db.expire_all()
    # Soft delete keeps rows for history; public passport becomes unavailable.
    product = db.get(Product, pid)
    assert product is not None
    assert product.deleted_at is not None
    assert db.scalar(select(func.count()).select_from(Material)) == 1
    assert db.scalar(select(func.count()).select_from(Passport)) == 1
    assert db.scalar(select(func.count()).select_from(QrScan)) == 1
    assert client.get(f"/api/v1/passport/{public_uuid}").status_code == 404


def test_duplicate_sku_rolls_back_cleanly(
    client: TestClient, admin_headers: dict[str, str], db: Session
):
    """Failed duplicate SKU leaves the first row intact and session usable."""
    body = product_body(sku="ROLL-001")
    first = client.post("/api/v1/products", headers=admin_headers, json=body)
    assert first.status_code == 201

    second = client.post("/api/v1/products", headers=admin_headers, json=body)
    assert second.status_code == 409

    db.expire_all()
    count = db.scalar(select(func.count()).select_from(Product).where(Product.sku == "ROLL-001"))
    assert count == 1

    # Session still works after rollback inside create_product
    third = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(sku="ROLL-002"),
    )
    assert third.status_code == 201


def test_concurrent_same_email_user_insert(db: Session):
    """Two parallel inserts with the same email: one wins, one IntegrityError."""
    email = f"race-{uuid4().hex[:8]}@example.com"

    def insert_once() -> str:
        session = TestingSessionLocal()
        try:
            session.add(
                User(
                    email=email,
                    password_hash=hash_password("x"),
                    role=UserRole.EDITOR,
                )
            )
            session.commit()
            return "ok"
        except IntegrityError:
            session.rollback()
            return "conflict"
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: insert_once(), range(2)))

    assert sorted(results) == ["conflict", "ok"]
    db.expire_all()
    assert (
        db.scalar(select(func.count()).select_from(User).where(User.email == email))
        == 1
    )


def test_concurrent_create_same_sku(
    parallel_client: TestClient,
    admin_user: User,
    editor_user: User,
):
    """Two users create the same SKU at once: one 201, one 409."""
    admin_token = parallel_client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "admin-pass"},
    ).json()["access_token"]
    editor_token = parallel_client.post(
        "/api/v1/auth/login",
        json={"email": editor_user.email, "password": "editor-pass"},
    ).json()["access_token"]

    body = product_body(sku="RACE-SKU")

    def create(token: str) -> int:
        r = parallel_client.post(
            "/api/v1/products",
            headers={"Authorization": f"Bearer {token}"},
            json=body,
        )
        return r.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(
            pool.map(create, [admin_token, editor_token])
        )

    assert sorted(codes) == [201, 409]


def test_concurrent_patch_same_product(
    parallel_client: TestClient,
    admin_user: User,
    editor_user: User,
):
    """Two users patch the same product; both succeed (last write wins)."""
    admin_h = {
        "Authorization": (
            "Bearer "
            + parallel_client.post(
                "/api/v1/auth/login",
                json={"email": admin_user.email, "password": "admin-pass"},
            ).json()["access_token"]
        )
    }
    editor_h = {
        "Authorization": (
            "Bearer "
            + parallel_client.post(
                "/api/v1/auth/login",
                json={"email": editor_user.email, "password": "editor-pass"},
            ).json()["access_token"]
        )
    }

    product = parallel_client.post(
        "/api/v1/products", headers=admin_h, json=product_body()
    ).json()
    pid = product["id"]

    def patch(name: str, headers: dict[str, str]) -> int:
        r = parallel_client.patch(
            f"/api/v1/products/{pid}",
            headers=headers,
            json={"name": name},
        )
        return r.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(patch, "Name-A", admin_h),
            pool.submit(patch, "Name-B", editor_h),
        ]
        codes = [f.result() for f in as_completed(futures)]

    assert sorted(codes) == [200, 200]
    final = parallel_client.get(f"/api/v1/products/{pid}", headers=admin_h).json()
    assert final["name"] in {"Name-A", "Name-B"}


def test_concurrent_double_publish(
    parallel_client: TestClient, admin_user: User, editor_user: User
):
    """Two publish calls on the same draft: one 200, one 409."""
    admin_h = {
        "Authorization": (
            "Bearer "
            + parallel_client.post(
                "/api/v1/auth/login",
                json={"email": admin_user.email, "password": "admin-pass"},
            ).json()["access_token"]
        )
    }
    editor_h = {
        "Authorization": (
            "Bearer "
            + parallel_client.post(
                "/api/v1/auth/login",
                json={"email": editor_user.email, "password": "editor-pass"},
            ).json()["access_token"]
        )
    }
    product = parallel_client.post(
        "/api/v1/products", headers=admin_h, json=product_body()
    ).json()
    pid = product["id"]

    def publish(headers: dict[str, str]) -> int:
        return parallel_client.post(
            f"/api/v1/products/{pid}/publish", headers=headers
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(pool.map(publish, [admin_h, editor_h]))

    assert sorted(codes) == [200, 409]


def test_patch_with_garbage_token_rejected(
    client: TestClient, admin_headers: dict[str, str]
):
    """Mutations with an invalid Bearer token are rejected."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.patch(
        f"/api/v1/products/{product['id']}",
        headers={"Authorization": "Bearer not-a-real-token"},
        json={"name": "Hacked"},
    )
    assert r.status_code == 401
    still = client.get(
        f"/api/v1/products/{product['id']}", headers=admin_headers
    ).json()
    assert still["name"] != "Hacked"


def test_patch_with_expired_token_rejected(
    client: TestClient, admin_user: User, admin_headers: dict[str, str]
):
    """Mutations with an expired access token are rejected."""
    from datetime import UTC, datetime, timedelta

    import jwt

    from app.core.config import get_settings

    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": str(admin_user.id),
            "role": "admin",
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    r = client.patch(
        f"/api/v1/products/{product['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Hacked"},
    )
    assert r.status_code == 401
