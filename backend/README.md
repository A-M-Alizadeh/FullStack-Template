# Backend

FastAPI API for the DPP platform.

## Layout

```
app/
  api/         route aggregation
  core/        config, logging, middleware, enums
  auth/        login, JWT, refresh, deps
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

## Next

1. Publish / QR / public passport / scans
2. Dashboard + analytics
3. Tests, then frontend

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

Demo product SKU: `DEMO-001` (draft, with materials / sustainability / cert / doc / cover).

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

Docs: http://localhost:8000/docs
