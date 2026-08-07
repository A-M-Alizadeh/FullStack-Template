# Backend

FastAPI API for the DPP platform.

## Layout

```
app/
  api/         route aggregation
  core/        config, logging, middleware, enums
  auth/        login, JWT, refresh, deps
  passport/    publish, public passport, scans
  schemas/     Pydantic request/response models
  users/       User model
  products/    product + nested models
  database/    engine, session, Base
alembic/
scripts/       seed helpers
tests/
```

## Done so far

1. Project split, env config, FastAPI core, health.
2. DB design, models, Alembic, tables in Postgres.
3. Auth: login / refresh / logout / me, bcrypt, JWT access + hashed refresh tokens, role deps.
4. Product CRUD (draft create; publish comes later).
5. Nested product data: materials, sustainability, certifications, documents, images.
6. Publish + QR + public passport + scan tracking.

## Next

1. Dashboard + analytics
2. Tests, then frontend

## Run

```bash
docker compose up db
cd backend
APP_ENV=local uv run alembic upgrade head
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run python -m scripts.seed_lookups
APP_ENV=local uv run python -m scripts.seed_products
APP_ENV=local uv run uvicorn app.main:app --reload
```

Seed users (dev only):

- `admin@example.com` / `admin1234`
- `editor@example.com` / `editor1234`

Demo product SKU: `DEMO-001` (draft until you publish it).

Auth:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me` (Bearer access token)

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

Docs: http://localhost:8000/docs
