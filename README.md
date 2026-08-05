# Digital Product Passport

Full-stack app for creating and publishing digital product passports (QR → public page).

## Structure

- `backend/` — FastAPI
- `frontend/` — Next.js
- `docker-compose.yml` — local (db + api + web)
- `docker-compose.prod.yml` — prod overrides

See `backend/README.md` and `frontend/README.md` for app-specific notes.

## Setup

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local
```

Edit secrets before running.

## Run

```bash
docker compose up --build
```

Without Docker:

```bash
cd backend && uv sync && APP_ENV=local uv run uvicorn app.main:app --reload
cd frontend && npm i && npm run dev
```

- API: http://localhost:8000/docs
- App: http://localhost:3000

Prod-style:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file frontend/.env.production up --build -d
```
