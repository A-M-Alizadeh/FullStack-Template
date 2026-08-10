# Backend

FastAPI API for the Digital Product Passport platform.

Architecture: [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) · Overview PDF: [`../docs/DPP_Project_Overview.pdf`](../docs/DPP_Project_Overview.pdf)

## Layout

```
app/
  api/         route aggregation
  core/        config, storage, cache, logging
  auth/        login, JWT, refresh, deps
  users/       admin user CRUD
  products/    product + nested resources
  passport/    publish, public passport, PDF, scans
  dashboard/   summary counts
  analytics/   scan stats
  audit/       append-only audit trail
  schemas/     Pydantic models
  database/    engine, session, Base
alembic/       migrations
scripts/       seeds, purge, overview PDF
tests/
```

## Run

```bash
docker compose up db          # from repo root; add redis minio if needed
cd backend
uv sync
APP_ENV=local uv run alembic upgrade head
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run python -m scripts.seed_lookups
APP_ENV=local uv run python -m scripts.seed_products
APP_ENV=local uv run python -m scripts.seed_scans
APP_ENV=local uv run python -m scripts.seed_audit
APP_ENV=local uv run uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs

### Optional env

| Variable | Purpose |
|----------|---------|
| `REDIS_URL` | Dashboard/analytics cache (empty = off) |
| `STORAGE_BACKEND` | `local` (default) or `minio` |
| `SOFT_DELETE_RETENTION_DAYS` | Days before soft-deleted products can be purged (default 30) |

## Seeds & jobs

| Command | What it does |
|---------|----------------|
| `scripts.seed_users` | admin / editor demo accounts |
| `scripts.seed_lookups` | cert types & authorities |
| `scripts.seed_products` | `DEMO-001` + nested demo files |
| `scripts.seed_scans` | publish + republish, PDF cache, QR scans |
| `scripts.seed_audit` | sample audit rows if empty |
| `scripts.purge_deleted_products` | hard-delete old soft-deleted products + files |
| `scripts.generate_overview_pdf` | write `docs/DPP_Project_Overview.pdf` |

```bash
APP_ENV=local uv run python -m scripts.purge_deleted_products --dry-run
APP_ENV=local uv run python -m scripts.purge_deleted_products --days 30
```

## Main APIs

**Auth:** `POST /auth/login|refresh|logout`, `GET /auth/me`  
**Products:** CRUD, nested materials/sustainability/certs/docs/images, soft delete + restore  
**Publish:** `POST /products/{id}/publish`, versions, QR PNG  
**Public:** `GET /passport/{uuid}`, `?src=qr`, `/pdf`, media files  
**Ops:** dashboard, analytics, audit (admin), users (admin)

## Tests

Uses DB `dpp_test` (auto-created). Needs Postgres:

```bash
docker compose up db
APP_ENV=local uv run pytest
```

## Seed logins

- `admin@example.com` / `admin1234`
- `editor@example.com` / `editor1234`
