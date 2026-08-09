"""Admin user CRUD + role gating."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.users.models import User
from tests.conftest import product_body


def test_unauthenticated_users_rejected(client: TestClient):
    assert client.get("/api/v1/users").status_code == 401


def test_editor_cannot_list_users(
    client: TestClient, editor_headers: dict[str, str]
):
    r = client.get("/api/v1/users", headers=editor_headers)
    assert r.status_code == 403


def test_editor_cannot_mutate_users(
    client: TestClient,
    editor_user: User,
    editor_headers: dict[str, str],
    admin_user: User,
):
    create = client.post(
        "/api/v1/users",
        headers=editor_headers,
        json={
            "email": "blocked@example.com",
            "password": "password12",
            "role": "editor",
        },
    )
    assert create.status_code == 403

    patch = client.patch(
        f"/api/v1/users/{admin_user.id}",
        headers=editor_headers,
        json={"role": "editor"},
    )
    assert patch.status_code == 403

    delete = client.delete(
        f"/api/v1/users/{admin_user.id}", headers=editor_headers
    )
    assert delete.status_code == 403
    # editor still exists; target admin untouched
    assert editor_user.email == "editor@example.com"


def test_admin_user_crud(
    client: TestClient,
    admin_user: User,
    admin_headers: dict[str, str],
):
    created = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "email": "newbie@example.com",
            "password": "password12",
            "role": "editor",
        },
    )
    assert created.status_code == 201
    user = created.json()
    assert user["email"] == "newbie@example.com"
    assert user["role"] == "editor"
    user_id = user["id"]

    listed = client.get("/api/v1/users", headers=admin_headers)
    assert listed.status_code == 200
    emails = {u["email"] for u in listed.json()}
    assert "newbie@example.com" in emails
    assert admin_user.email in emails

    patched = client.patch(
        f"/api/v1/users/{user_id}",
        headers=admin_headers,
        json={"role": "admin", "password": "password99"},
    )
    assert patched.status_code == 200
    assert patched.json()["role"] == "admin"

    deleted = client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
    assert deleted.status_code == 204

    listed_after = client.get("/api/v1/users", headers=admin_headers)
    assert "newbie@example.com" not in {u["email"] for u in listed_after.json()}


def test_cannot_delete_self(
    client: TestClient, admin_user: User, admin_headers: dict[str, str]
):
    r = client.delete(f"/api/v1/users/{admin_user.id}", headers=admin_headers)
    assert r.status_code == 400
    assert "own" in r.json()["detail"].lower()


def test_cannot_demote_last_admin(
    client: TestClient, admin_user: User, admin_headers: dict[str, str]
):
    r = client.patch(
        f"/api/v1/users/{admin_user.id}",
        headers=admin_headers,
        json={"role": "editor"},
    )
    assert r.status_code == 400
    assert "last admin" in r.json()["detail"].lower()


def test_cannot_delete_user_with_products(
    client: TestClient,
    admin_headers: dict[str, str],
):
    owner = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "email": "owner@example.com",
            "password": "password12",
            "role": "admin",
        },
    ).json()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "password12"},
    )
    assert login.status_code == 200
    owner_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    product = client.post(
        "/api/v1/products",
        headers=owner_headers,
        json=product_body(sku="OWNED-001"),
    )
    assert product.status_code == 201

    r = client.delete(f"/api/v1/users/{owner['id']}", headers=admin_headers)
    assert r.status_code == 409
    assert "product" in r.json()["detail"].lower()


def test_duplicate_email(
    client: TestClient, admin_user: User, admin_headers: dict[str, str]
):
    r = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "email": admin_user.email,
            "password": "password12",
            "role": "editor",
        },
    )
    assert r.status_code == 409


def test_short_password_rejected(
    client: TestClient, admin_headers: dict[str, str]
):
    r = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "email": "short@example.com",
            "password": "short",
            "role": "editor",
        },
    )
    assert r.status_code == 422


def test_update_user_not_found(
    client: TestClient, admin_headers: dict[str, str]
):
    r = client.patch(
        f"/api/v1/users/{uuid4()}",
        headers=admin_headers,
        json={"email": "ghost@example.com"},
    )
    assert r.status_code == 404
