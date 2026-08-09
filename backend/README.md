# Backend

FastAPI API for the DPP platform.

## Layout

```
app/
  api/         route aggregation
  core/        config, logging, middleware, enums
  auth/        login, JWT, refresh, deps
  passport/    publish, public passport, scans
  dashboard/   summary counts
  analytics/   scan stats
  schemas/     Pydantic request/response models
  users/       User model
  products/    product + nested models
  database/    engine, session, Base
alembic/
scripts/       seed helpers
tests/
```

## Status

Auth (JWT access + httpOnly refresh cookie), product CRUD + nested resources, publish/QR, public passport + scan tracking, dashboard, analytics, seeds, unit/integration tests.

Swagger: `/docs` (tags: `products`, `materials`, `publish`, `passport`, …).

Frontend lives in `../frontend`.

## Tests

Uses a separate Postgres DB `dpp_test` (created automatically).

```bash
docker compose up db
cd backend
APP_ENV=local uv run pytest
```

## Run

```bash
docker compose up db
cd backend
APP_ENV=local uv run alembic upgrade head
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run python -m scripts.seed_lookups
APP_ENV=local uv run python -m scripts.seed_products
APP_ENV=local uv run python -m scripts.seed_scans
APP_ENV=local uv run uvicorn app.main:app --reload
```

Seed users (dev only):

- `admin@example.com` / `admin1234`
- `editor@example.com` / `editor1234`

Demo product SKU: `DEMO-001`. `seed_scans` publishes it (if needed) and adds sample QR scans for dashboard/analytics.

Auth:

- `POST /api/v1/auth/login` — access JWT in JSON; refresh in httpOnly cookie
- `POST /api/v1/auth/refresh` — cookie (or optional body); new access + rotated cookie
- `POST /api/v1/auth/logout` — revoke + clear cookie
- `GET /api/v1/auth/me` — Bearer access token

Frontend must call auth with `credentials: "include"`. Access token stays in memory; refresh is cookie-only.

Products (admin or editor):

- `GET/POST /api/v1/products`
- `GET/PATCH/DELETE /api/v1/products/{id}`
- Materials / sustainability / certifications / documents / images under `/api/v1/products/{id}/...`
- Lookups: `GET /api/v1/products/certification-types`, `GET /api/v1/products/issuing-authorities`
- `POST /api/v1/products/{id}/publish`
- `GET /api/v1/products/{id}/passport/qr`

Public:

- `GET /api/v1/passport/{uuid}` (no auth)
- `GET /api/v1/passport/{uuid}?src=qr` — same data; also records a QR scan
- File downloads under `/api/v1/passport/{uuid}/.../file`

QR codes encode `{FRONTEND_URL}/passport/{uuid}?src=qr`. The frontend should forward `src` to the API when loading the page.

Dashboard / analytics (admin or editor):

- `GET /api/v1/dashboard`
- `GET /api/v1/analytics`

Docs: http://localhost:8000/docs
