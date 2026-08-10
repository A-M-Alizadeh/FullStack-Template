# Backend

FastAPI API for the Digital Product Passport.

Report: [`../docs/REPORT.md`](../docs/REPORT.md) · Architecture: [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)

## Run (local)

```bash
docker compose up db   # from repo root
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

Logins: `admin@example.com` / `admin1234` · `editor@example.com` / `editor1234`

## Production process

Docker / deploy uses Gunicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 app.main:app
```

(`WEB_CONCURRENCY` in the Dockerfile sets `-w`.)

## Useful scripts

| Script | Purpose |
|--------|---------|
| `seed_*` | Demo users, lookups, product, scans, audit |
| `seed_load` | Bulk `LOAD-*` products for stress |
| `stress_test` | Concurrent HTTP harness → `docs/load-results.md` |
| `purge_deleted_products` | Hard-delete soft-deleted rows past retention |
| `generate_overview_pdf` | Rebuild `docs/DPP_Project_Overview.pdf` |

```bash
APP_ENV=local uv run python -m scripts.seed_load --count 1000
APP_ENV=local uv run python -m scripts.stress_test --workers 20 --requests 200
APP_ENV=local uv run python -m scripts.purge_deleted_products --dry-run
```

## Config highlights

| Env | Meaning |
|-----|---------|
| `RATE_LIMIT_*` | Auth / public / API IP limits (`RATE_LIMIT_ENABLED=false` for pure load) |
| `MAX_UPLOAD_BYTES` | Upload size cap |
| `SOFT_DELETE_RETENTION_DAYS` | Purge eligibility |
| `REDIS_URL` / `STORAGE_BACKEND` | Optional cache / MinIO |

## Tests

```bash
docker compose up db
APP_ENV=local uv run pytest
```

Uses DB `dpp_test` (created automatically).
