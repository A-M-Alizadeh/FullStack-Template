"""Soft-delete retention purge."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.storage import LocalStorage
from app.products import service as products_service
from app.products.models import Product
from tests.conftest import product_body


def test_purge_removes_old_soft_deleted_product(
    client: TestClient,
    admin_headers: dict[str, str],
    db: Session,
    storage: LocalStorage,
):
    created = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(sku="PURGE-OLD"),
    ).json()
    product_id = UUID(created["id"])
    assert (
        client.delete(
            f"/api/v1/products/{product_id}", headers=admin_headers
        ).status_code
        == 204
    )

    product = db.get(Product, product_id)
    assert product is not None
    product.deleted_at = datetime.now(UTC) - timedelta(days=45)
    db.commit()

    purged = products_service.purge_soft_deleted_products(
        db, storage=storage, older_than_days=30
    )
    assert product_id in purged
    db.expire_all()
    assert db.get(Product, product_id) is None


def test_purge_skips_recent_soft_deleted_product(
    client: TestClient,
    admin_headers: dict[str, str],
    db: Session,
    storage: LocalStorage,
):
    created = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(sku="PURGE-NEW"),
    ).json()
    product_id = UUID(created["id"])
    assert (
        client.delete(
            f"/api/v1/products/{product_id}", headers=admin_headers
        ).status_code
        == 204
    )

    purged = products_service.purge_soft_deleted_products(
        db, storage=storage, older_than_days=30
    )
    assert product_id not in purged
    assert db.get(Product, product_id) is not None


def test_purge_dry_run_keeps_row(
    client: TestClient,
    admin_headers: dict[str, str],
    db: Session,
    storage: LocalStorage,
):
    created = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(sku="PURGE-DRY"),
    ).json()
    product_id = UUID(created["id"])
    assert (
        client.delete(
            f"/api/v1/products/{product_id}", headers=admin_headers
        ).status_code
        == 204
    )
    product = db.get(Product, product_id)
    assert product is not None
    product.deleted_at = datetime.now(UTC) - timedelta(days=60)
    db.commit()

    purged = products_service.purge_soft_deleted_products(
        db, storage=storage, older_than_days=30, dry_run=True
    )
    assert product_id in purged
    assert db.get(Product, product_id) is not None
