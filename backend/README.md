# Backend

FastAPI API for the DPP platform.

## Layout

```
app/
  api/        routers
  core/       config, logging, middleware, errors, enums
  auth/       (todo)
  users/      User model
  products/   product + nested models
  database/   engine, session, Base
alembic/
tests/
```

## What we did so far

1. Split backend from frontend, Compose at repo root.
2. Config from env files via `APP_ENV`.
3. App factory, middleware, health route.
4. DB plan in [docs/database.md](docs/database.md).
5. SQLAlchemy models + Alembic initial migration.
6. Postgres in Docker + `alembic upgrade head` (tables created).

## Next

1. **Auth (JWT, admin / editor)** — schemas, login, password hash, route deps
2. **Products + nested APIs** — CRUD + materials / sustainability / certs / docs / images
3. **Publish / QR / public passport / scans**
4. **Dashboard + analytics**
5. **Seed + tests**, then frontend

## Run

```bash
# repo root — start DB
docker compose up db

# backend — create tables
APP_ENV=local uv run alembic upgrade head

APP_ENV=local uv run uvicorn app.main:app --reload
```
