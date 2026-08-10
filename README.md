# Digital Product Passport

Create, publish, and share digital product passports (QR → public page).

| Layer | Tech |
|-------|------|
| Backend | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL |
| Frontend | Next.js, TypeScript, MUI, RTK Query |
| Local infra | Docker Compose Postgres (`redis` / `minio` optional) |

More detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [`docs/DPP_Project_Overview.pdf`](docs/DPP_Project_Overview.pdf) · [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md)

## Setup

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local
```

## Run locally

```bash
docker compose up db
```

```bash
# terminal A — API
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

```bash
# terminal B — web
cd frontend
npm i
npm run dev
```

- App: http://localhost:3000  
- API / Swagger: http://localhost:8000/docs  

Optional: `docker compose up db redis minio` and set `REDIS_URL` / `STORAGE_BACKEND=minio` in `backend/.env.local`.

## Seed logins

| Email | Password | Role |
|-------|----------|------|
| `admin@example.com` | `admin1234` | admin |
| `editor@example.com` | `editor1234` | editor |

Demo product: `DEMO-001` (published, version history, PDF, sample scans).

## Features

- JWT access + httpOnly refresh; roles `admin` / `editor`
- Product CRUD + nested resources; publish / republish (stable UUID + QR)
- Public passport, PDF download, QR scan analytics
- Soft delete + Undo; purge job after retention (`scripts.purge_deleted_products`)
- Search / pagination, audit log, drag-and-drop uploads
- Optional Redis cache and MinIO storage

## Tests

```bash
cd backend && APP_ENV=local uv run pytest
cd frontend && npm test
cd frontend && npm run test:e2e   # API + seeded DB running
```

## Soft-delete purge

```bash
cd backend
APP_ENV=local uv run python -m scripts.purge_deleted_products --dry-run
APP_ENV=local uv run python -m scripts.purge_deleted_products --days 30
```

Retention defaults to `SOFT_DELETE_RETENTION_DAYS=30`.

## Regenerate overview PDF

```bash
cd backend && APP_ENV=local uv run python -m scripts.generate_overview_pdf
```
