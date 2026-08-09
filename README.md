# Digital Product Passport

Full-stack app for creating and publishing digital product passports (QR → public page).

## Structure

- `backend/` — FastAPI (auth, products, publish/QR, passport, dashboard, analytics, users)
- `frontend/` — Next.js back office + public passport page
- `docs/ARCHITECTURE.md` — system design, DB, security, scalability
- `docker-compose.yml` — **Postgres for local dev** (API/web Docker services are commented out; use host processes below)
- `docker-compose.prod.yml` — prod overrides when you enable full Compose

See `backend/README.md` and `frontend/README.md` for app-specific notes.

## Setup

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local
```

## Local development

Postgres in Docker; API and web on the host:

```bash
docker compose up db
```

```bash
# terminal A
cd backend && uv sync && APP_ENV=local uv run alembic upgrade head
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run python -m scripts.seed_lookups
APP_ENV=local uv run python -m scripts.seed_products
APP_ENV=local uv run python -m scripts.seed_scans
APP_ENV=local uv run uvicorn app.main:app --reload

# terminal B
cd frontend && npm i && npm run dev
```

- API / Swagger: http://localhost:8000/docs
- App: http://localhost:3000

`backend/.env.local` uses `POSTGRES_HOST=localhost` so the host API reaches the Compose DB.

### Full stack in Docker (optional)

`backend/Dockerfile` and `frontend/Dockerfile` are ready. Uncomment the `backend` and `frontend` services in `docker-compose.yml`, set env files, then:

```bash
docker compose up --build
```

## What’s in place

**Backend**

- JWT access + httpOnly refresh cookie
- Products + materials / sustainability / certifications / documents / images
- Publish → public UUID + QR PNG; public passport + QR scan tracking
- Dashboard + analytics
- Admin-only user CRUD
- Seeds + Pytest (unit + integration)

**Frontend**

- Login / session bootstrap
- Back office: Dashboard, Products, Product Passports, Analytics, Users (admin), Settings
- Product editor tabs + Preview; product list with cover, QR modal, views
- Public passport with brand mark; EN/IT + light/dark settings
- Vitest/RTL + Playwright smoke (incl. admin vs editor Users nav)

## Tests

```bash
# backend (needs Postgres; uses dpp_test)
cd backend && APP_ENV=local uv run pytest

# frontend unit
cd frontend && npm test

# frontend e2e (API + seeded DB running)
cd frontend && npm run test:e2e
```

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Database notes / ERD](backend/docs/database.md)

## Seed logins (dev only)

| Email | Password | Role |
|-------|----------|------|
| `admin@example.com` | `admin1234` | admin |
| `editor@example.com` | `editor1234` | editor |
