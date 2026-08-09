# Digital Product Passport

Full-stack app for creating and publishing digital product passports (QR → public page).

## Structure

- `backend/` — FastAPI
- `frontend/` — Next.js
- `docker-compose.yml` — Postgres for local dev (API/web services commented out)
- `docker-compose.prod.yml` — prod overrides

See `backend/README.md` and `frontend/README.md` for app-specific notes.

## Setup

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local
```

## Local development

Postgres in Docker, API and web on the host (usual setup):

```bash
docker compose up db
```

```bash
cd backend && uv sync && APP_ENV=local uv run uvicorn app.main:app --reload
cd frontend && npm i && npm run dev
```

- API: http://localhost:8000/docs
- App: http://localhost:3000

`backend/.env.local` already uses `POSTGRES_HOST=localhost`.

## What’s in place

- Backend: auth (cookie refresh), products + nested resources, publish/QR, public passport, dashboard, analytics, seeds, tests
- Frontend: login, back-office (dashboard / products / analytics), public passport page

See `backend/README.md` and `frontend/README.md` for details.
