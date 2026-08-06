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

## Next

1. Products + nested APIs
2. Publish / QR / public passport / scans
3. Dashboard + analytics
4. More seed + tests, then frontend

## Run

```bash
docker compose up db
cd backend
APP_ENV=local uv run alembic upgrade head
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run uvicorn app.main:app --reload
```

Seed users (dev only):

- `admin@example.com` / `admin1234`
- `editor@example.com` / `editor1234`

Auth:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me` (Bearer access token)

Docs: http://localhost:8000/docs
