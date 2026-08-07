"""Publish, public passport, QR scans."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.products.models import QrScan
from tests.conftest import product_body


def _create_and_publish(
    client: TestClient, headers: dict[str, str]
) -> tuple[str, str]:
    product = client.post(
        "/api/v1/products", headers=headers, json=product_body()
    ).json()
    published = client.post(
        f"/api/v1/products/{product['id']}/publish", headers=headers
    )
    assert published.status_code == 200
    return product["id"], published.json()["passport"]["public_uuid"]


def test_publish_ok(client: TestClient, admin_headers: dict[str, str]):
    """Publish creates an active passport and sets product published."""
    product_id, public_uuid = _create_and_publish(client, admin_headers)
    product = client.get(
        f"/api/v1/products/{product_id}", headers=admin_headers
    ).json()
    assert product["status"] == "published"
    assert public_uuid


def test_publish_twice_conflict(client: TestClient, admin_headers: dict[str, str]):
    """Publishing an already published product returns 409."""
    product_id, _ = _create_and_publish(client, admin_headers)
    r = client.post(
        f"/api/v1/products/{product_id}/publish", headers=admin_headers
    )
    assert r.status_code == 409


def test_qr_before_publish(client: TestClient, admin_headers: dict[str, str]):
    """QR endpoint before publish returns 404."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.get(
        f"/api/v1/products/{product['id']}/passport/qr",
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_qr_after_publish(client: TestClient, admin_headers: dict[str, str]):
    """QR endpoint after publish returns a PNG."""
    product_id, _ = _create_and_publish(client, admin_headers)
    r = client.get(
        f"/api/v1/products/{product_id}/passport/qr",
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.content.startswith(b"\x89PNG")


def test_public_passport_ok(client: TestClient, admin_headers: dict[str, str]):
    """Public passport is readable without auth."""
    _, public_uuid = _create_and_publish(client, admin_headers)
    r = client.get(f"/api/v1/passport/{public_uuid}")
    assert r.status_code == 200
    assert r.json()["public_uuid"] == public_uuid


def test_public_passport_unknown(client: TestClient):
    """Unknown public UUID returns 404."""
    r = client.get(f"/api/v1/passport/{uuid4()}")
    assert r.status_code == 404


def test_scan_only_with_src_qr(
    client: TestClient, admin_headers: dict[str, str], db: Session
):
    """Direct open does not create a scan; src=qr creates one."""
    _, public_uuid = _create_and_publish(client, admin_headers)

    assert client.get(f"/api/v1/passport/{public_uuid}").status_code == 200
    count_after_direct = db.scalar(select(func.count()).select_from(QrScan)) or 0
    assert count_after_direct == 0

    assert (
        client.get(f"/api/v1/passport/{public_uuid}", params={"src": "qr"}).status_code
        == 200
    )
    # expire session cache so count sees the committed row
    db.expire_all()
    count_after_qr = db.scalar(select(func.count()).select_from(QrScan)) or 0
    assert count_after_qr == 1


def test_public_file_unknown_ids(
    client: TestClient, admin_headers: dict[str, str]
):
    """Public file download with random ids returns 404."""
    _, public_uuid = _create_and_publish(client, admin_headers)
    r = client.get(
        f"/api/v1/passport/{public_uuid}/documents/{uuid4()}/file"
    )
    assert r.status_code == 404
