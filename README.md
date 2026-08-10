# Digital Product Passport

Full-stack app to create, publish, and share digital product passports (QR → public page).

| | |
|--|--|
| Backend | FastAPI, SQLAlchemy, Alembic, PostgreSQL, Gunicorn |
| Frontend | Next.js, TypeScript, MUI, RTK Query |
| Docs | [Project report](docs/REPORT.md) · [Architecture](docs/ARCHITECTURE.md) · [Overview PDF](docs/DPP_Project_Overview.pdf) |

## Quick start

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local

docker compose up db
```

**API** (terminal A):

```bash
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

**Web** (terminal B):

```bash
cd frontend
npm i
npm run dev
```

- App: http://localhost:3000  
- Swagger: http://localhost:8000/docs  

| Email | Password | Role |
|-------|----------|------|
| `admin@example.com` | `admin1234` | admin |
| `editor@example.com` | `editor1234` | editor |

Optional: `docker compose up db redis minio` and set `REDIS_URL` / `STORAGE_BACKEND=minio`.

## What’s included

Auth (JWT + httpOnly refresh), products + nested resources, publish/republish + QR, public passport + PDF, dashboard/analytics, soft delete + purge, audit, rate limits, upload hardening, optional Redis/MinIO.

Details and decisions: **[docs/REPORT.md](docs/REPORT.md)**.

## Load / stress

```bash
# terminal A: keep API running
cd backend && APP_ENV=local uv run uvicorn app.main:app --reload

# terminal B (gentle defaults: 8 workers, 80 requests)
cd backend && APP_ENV=local uv run python -m scripts.stress_test
```

See [docs/load-results.md](docs/load-results.md).

## Tests

```bash
cd backend && APP_ENV=local uv run pytest
cd frontend && npm test
```

CI runs on pushes/PRs to `main`/`master` (GitHub Actions).

## Deploy

Free live demo: **Neon** (Postgres) + **Render** free web (API) + **Vercel** (frontend).

Step-by-step: **[docs/DEPLOY.md](docs/DEPLOY.md)** · Blueprint: [`render.yaml`](render.yaml)
