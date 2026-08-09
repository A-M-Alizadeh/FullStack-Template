"""Admin audit trail."""

from fastapi.testclient import TestClient

from tests.conftest import product_body


def test_editor_cannot_list_audit(
    client: TestClient, editor_headers: dict[str, str]
):
    assert client.get("/api/v1/audit", headers=editor_headers).status_code == 403


def test_audit_records_product_lifecycle(
    client: TestClient, admin_headers: dict[str, str]
):
    created = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Audited", sku="AUD-001"),
    )
    assert created.status_code == 201
    product_id = created.json()["id"]

    assert (
        client.delete(
            f"/api/v1/products/{product_id}", headers=admin_headers
        ).status_code
        == 204
    )
    assert (
        client.post(
            f"/api/v1/products/{product_id}/restore", headers=admin_headers
        ).status_code
        == 200
    )

    logs = client.get("/api/v1/audit", headers=admin_headers)
    assert logs.status_code == 200
    actions = {row["action"] for row in logs.json()["items"]}
    assert "product.create" in actions
    assert "product.delete" in actions
    assert "product.restore" in actions


def test_audit_records_publish_and_republish(
    client: TestClient, admin_headers: dict[str, str]
):
    product = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json=product_body(name="Publish Audit", sku="AUD-PUB-1"),
    ).json()
    assert (
        client.post(
            f"/api/v1/products/{product['id']}/publish", headers=admin_headers
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/products/{product['id']}/publish", headers=admin_headers
        ).status_code
        == 200
    )

    logs = client.get("/api/v1/audit", headers=admin_headers).json()["items"]
    actions = {row["action"] for row in logs}
    assert "product.publish" in actions
    assert "product.republish" in actions
