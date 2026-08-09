"""Product CRUD and nested resource API."""

from __future__ import annotations

from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import product_body


def test_product_crud(client: TestClient, admin_headers: dict[str, str]):
    """Create, list, get, patch, delete a draft product."""
    created = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Widget"),
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    assert created.json()["status"] == "draft"

    listed = client.get("/api/v1/products", headers=admin_headers)
    assert listed.status_code == 200
    body = listed.json()
    assert "items" in body and "total" in body
    assert any(p["id"] == product_id for p in body["items"])

    got = client.get(f"/api/v1/products/{product_id}", headers=admin_headers)
    assert got.status_code == 200
    assert got.json()["name"] == "Widget"

    patched = client.patch(
        f"/api/v1/products/{product_id}",
        headers=admin_headers,
        json={"name": "Widget v2"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Widget v2"

    deleted = client.delete(f"/api/v1/products/{product_id}", headers=admin_headers)
    assert deleted.status_code == 204

    # Soft-delete: hidden from get/list; SKU can be reused.
    assert (
        client.get(f"/api/v1/products/{product_id}", headers=admin_headers).status_code
        == 404
    )
    listed_after = client.get("/api/v1/products", headers=admin_headers).json()
    assert all(p["id"] != product_id for p in listed_after["items"])
    # Restore brings it back (before SKU reuse).
    # Soft-deleted SKU is free — create a sibling then restore original would 409;
    # restore first while SKU is free:
    restored = client.post(
        f"/api/v1/products/{product_id}/restore",
        headers=admin_headers,
    )
    assert restored.status_code == 200
    assert (
        client.get(f"/api/v1/products/{product_id}", headers=admin_headers).status_code
        == 200
    )

    # Soft-delete again; SKU can be reused on a new product.
    assert (
        client.delete(
            f"/api/v1/products/{product_id}", headers=admin_headers
        ).status_code
        == 204
    )
    recreate = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Widget again", sku=created.json()["sku"]),
    )
    assert recreate.status_code == 201

    # Restore fails when SKU is taken by the new product.
    conflict = client.post(
        f"/api/v1/products/{product_id}/restore",
        headers=admin_headers,
    )
    assert conflict.status_code == 409


def test_products_require_auth(client: TestClient):
    """Product list without token is rejected."""
    r = client.get("/api/v1/products")
    assert r.status_code in (401, 403)


def test_product_not_found(client: TestClient, admin_headers: dict[str, str]):
    """Unknown product id returns 404."""
    r = client.get(f"/api/v1/products/{uuid4()}", headers=admin_headers)
    assert r.status_code == 404


def test_duplicate_sku(client: TestClient, admin_headers: dict[str, str]):
    """Second product with the same SKU returns 409."""
    body = product_body(sku="DUP-001")
    assert client.post("/api/v1/products", headers=admin_headers, json=body).status_code == 201
    r = client.post("/api/v1/products", headers=admin_headers, json=body)
    assert r.status_code == 409


def test_empty_name_rejected(client: TestClient, admin_headers: dict[str, str]):
    """Empty product name returns 422."""
    r = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="   "),
    )
    assert r.status_code == 422


def test_bad_category_rejected(client: TestClient, admin_headers: dict[str, str]):
    """Invalid category returns 422."""
    r = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(category="spaceship"),
    )
    assert r.status_code == 422


def test_bad_country_rejected(client: TestClient, admin_headers: dict[str, str]):
    """Invalid country code returns 422."""
    r = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(country_of_origin="DEU"),
    )
    assert r.status_code == 422


def test_material_and_wrong_product(
    client: TestClient, admin_headers: dict[str, str]
):
    """Material from product A is not found under product B."""
    a = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    b = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()

    mat = client.post(
        f"/api/v1/products/{a['id']}/materials",
        headers=admin_headers,
        json={
            "name": "Steel",
            "percentage": "40.00",
            "country_of_origin": "DE",
            "recyclable": True,
        },
    )
    assert mat.status_code == 201
    material_id = mat.json()["id"]

    r = client.patch(
        f"/api/v1/products/{b['id']}/materials/{material_id}",
        headers=admin_headers,
        json={"name": "Nope"},
    )
    assert r.status_code == 404


def test_sustainability_missing(client: TestClient, admin_headers: dict[str, str]):
    """GET sustainability before create returns 404."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.get(
        f"/api/v1/products/{product['id']}/sustainability",
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_cert_unknown_type(
    client: TestClient,
    admin_headers: dict[str, str],
    lookups: dict[str, str],
):
    """Unknown certification_type_id returns 400."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.post(
        f"/api/v1/products/{product['id']}/certifications",
        headers=admin_headers,
        data={
            "certification_type_id": str(uuid4()),
            "issuing_authority_id": lookups["issuing_authority_id"],
            "issue_date": "2024-01-01",
        },
        files={"pdf": ("cert.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf")},
    )
    assert r.status_code == 400


def test_cert_unknown_authority(
    client: TestClient,
    admin_headers: dict[str, str],
    lookups: dict[str, str],
):
    """Unknown issuing_authority_id returns 400."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.post(
        f"/api/v1/products/{product['id']}/certifications",
        headers=admin_headers,
        data={
            "certification_type_id": lookups["certification_type_id"],
            "issuing_authority_id": str(uuid4()),
            "issue_date": "2024-01-01",
        },
        files={"pdf": ("cert.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf")},
    )
    assert r.status_code == 400


def test_document_bad_file_type(client: TestClient, admin_headers: dict[str, str]):
    """Uploading a non-PDF document returns 400."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    r = client.post(
        f"/api/v1/products/{product['id']}/documents",
        headers=admin_headers,
        data={"doc_type": "user_manual"},
        files={"file": ("notes.exe", BytesIO(b"x"), "application/octet-stream")},
    )
    assert r.status_code == 400


def test_lookups_list(
    client: TestClient,
    admin_headers: dict[str, str],
    lookups: dict[str, str],
    db: Session,
):
    """Certification lookup endpoints return seeded rows."""
    types = client.get(
        "/api/v1/products/certification-types", headers=admin_headers
    )
    authorities = client.get(
        "/api/v1/products/issuing-authorities", headers=admin_headers
    )
    assert types.status_code == 200
    assert authorities.status_code == 200
    assert any(t["id"] == lookups["certification_type_id"] for t in types.json())
    assert any(
        a["id"] == lookups["issuing_authority_id"] for a in authorities.json()
    )


def test_editor_can_create_product(
    client: TestClient, editor_headers: dict[str, str]
):
    """Editor role can create products."""
    r = client.post(
        "/api/v1/products",
        headers=editor_headers,
        json=product_body(),
    )
    assert r.status_code == 201


def test_product_list_search_and_status(
    client: TestClient, admin_headers: dict[str, str]
):
    """List supports q search and status filter with pagination meta."""
    client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Alpha Searchable", sku="SEARCH-A"),
    )
    published = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Beta Other", sku="SEARCH-B"),
    ).json()
    assert (
        client.post(
            f"/api/v1/products/{published['id']}/publish",
            headers=admin_headers,
        ).status_code
        == 200
    )

    by_q = client.get(
        "/api/v1/products",
        headers=admin_headers,
        params={"q": "Alpha"},
    )
    assert by_q.status_code == 200
    assert by_q.json()["total"] >= 1
    assert all("Alpha" in p["name"] for p in by_q.json()["items"])

    by_status = client.get(
        "/api/v1/products",
        headers=admin_headers,
        params={"status": "published"},
    )
    assert by_status.status_code == 200
    assert by_status.json()["total"] >= 1
    assert all(p["status"] == "published" for p in by_status.json()["items"])

    page = client.get(
        "/api/v1/products",
        headers=admin_headers,
        params={"skip": 0, "limit": 1},
    )
    assert page.status_code == 200
    assert len(page.json()["items"]) == 1
    assert page.json()["limit"] == 1
    assert page.json()["total"] >= 2
