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
    assert any(p["id"] == product_id for p in listed.json())

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
