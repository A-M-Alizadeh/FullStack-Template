# Backend

FastAPI API for the DPP platform.

## Layout

```
app/
  api/        routers
  core/       config, logging, middleware, errors
  auth/       (todo)
  users/
  products/
  ...         domain modules per assessment
  database/   (todo)
alembic/
tests/
```

## What we did so far

1. Split backend from frontend, Compose at repo root.
2. Config from `.env.local` / `.env.production` via `APP_ENV` — no secrets in code. DB URL built from `POSTGRES_*`. Compose overrides `POSTGRES_HOST=db`.
3. App factory in `main.py`: CORS, request-id middleware, exception handlers, `/api/v1` router.
4. Health check only for now: `GET /api/v1/health`.
5. Logs go to stdout (enough for Docker logs). Skipping a log stack in Compose.

## Why

- Folder layout matches the brief so we can add domains without reshuffling.
- Env-based config keeps local/prod parallel.
- Product data stays in normal tables (materials, docs, etc. as separate rows). The public passport gets its own table with a UUID so the QR link does not break if we edit the product later.

## Next

- SQLAlchemy models + Alembic
- Auth (JWT, admin/editor)
- Products CRUD + nested data
- Publish / QR / public passport
- Dashboard + analytics
- Seed + tests

## Run

```bash
cp .env.local.example .env.local
uv sync
APP_ENV=local uv run uvicorn app.main:app --reload
```

```bash
APP_ENV=local uv run pytest
```
