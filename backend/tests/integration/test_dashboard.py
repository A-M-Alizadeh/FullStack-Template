"""Dashboard and analytics API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import product_body


def test_dashboard_requires_auth(client: TestClient):
    """Dashboard without token is rejected."""
    r = client.get("/api/v1/dashboard")
    assert r.status_code in (401, 403)


def test_analytics_requires_auth(client: TestClient):
    """Analytics without token is rejected."""
    r = client.get("/api/v1/analytics")
    assert r.status_code in (401, 403)


def test_dashboard_counts_after_publish_and_scan(
    client: TestClient, admin_headers: dict[str, str]
):
    """Dashboard totals reflect published passport and QR scans."""
    before = client.get("/api/v1/dashboard", headers=admin_headers).json()

    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    published = client.post(
        f"/api/v1/products/{product['id']}/publish", headers=admin_headers
    ).json()
    client.get(
        f"/api/v1/passport/{published['passport']['public_uuid']}",
        params={"src": "qr"},
    )

    after = client.get("/api/v1/dashboard", headers=admin_headers).json()
    assert after["total_products"] == before["total_products"] + 1
    assert after["published_passports"] == before["published_passports"] + 1
    assert after["generated_qr_codes"] == before["generated_qr_codes"] + 1
    assert after["total_passport_views"] == before["total_passport_views"] + 1


def test_analytics_after_scan(client: TestClient, admin_headers: dict[str, str]):
    """Analytics includes the published product after a QR scan."""
    product = client.post(
        "/api/v1/products", headers=admin_headers, json=product_body()
    ).json()
    published = client.post(
        f"/api/v1/products/{product['id']}/publish", headers=admin_headers
    ).json()
    client.get(
        f"/api/v1/passport/{published['passport']['public_uuid']}",
        params={"src": "qr"},
    )

    r = client.get("/api/v1/analytics", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["scans_today"] >= 1
    top = body["most_viewed_products"]
    assert any(p["product_id"] == product["id"] for p in top)
