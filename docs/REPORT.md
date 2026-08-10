# Digital Product Passport — Project Report

A short, practical write-up of what we built, why we chose it, and how to run and measure it.

## 1. Goal

Build a full-stack **Digital Product Passport (DPP)** platform: create product data in a back office, publish a stable public passport, share it via QR, and track scans for a simple analytics view.

## 2. Architecture

```
Browser (Next.js)
  ├─ Back office (JWT + refresh cookie)  →  FastAPI /api/v1/*  →  PostgreSQL
  │                                            └─ local disk or MinIO (files)
  └─ Public /passport/{uuid}  →  same API (optional ?src=qr → qr_scans)
```

| Layer | Choice | Why |
|-------|--------|-----|
| API | FastAPI + SQLAlchemy 2 + Alembic | Clear modules, typed schemas, migrations |
| DB | PostgreSQL | Relational product graph + enums + JSONB audit |
| Web | Next.js App Router + MUI + RTK Query | SPA UI talking to one OpenAPI backend |
| Auth | Access JWT + httpOnly refresh cookie | Short-lived access; refresh not in JS storage |
| Files | `Storage` protocol (local / MinIO) | Swap backends without rewriting routes |
| Cache | Optional Redis | Dashboard/analytics only; NullCache fallback |

Local default: Postgres in Docker; API and Next on the host. Prod Dockerfiles use **Gunicorn + Uvicorn workers** for the API.

## 3. Main design decisions

1. **Passport table separate from product** — QR links use a stable `public_uuid`. Republish keeps the UUID, bumps `version`, and revokes the previous row.
2. **Thin routers, fat services** — HTTP stays thin; publish, audit, purge, and PDF live in services (easier to test and extend).
3. **Shared editor workspace** — any `editor`/`admin` can manage products. Isolation is **role-based** + **object-key scoping**, not per-user tenancy.
4. **Soft delete first** — `deleted_at` hides rows; restore/Undo is cheap; a CLI purge hard-deletes after retention.
5. **Security without a platform** — rate limits, refresh reuse revoke, upload magic/size checks, product-scoped storage keys. No WAF/Celery required for the assessment.

## 4. Features

### Core
- Login / refresh / logout; roles `admin` | `editor`
- Product CRUD + materials, sustainability, certifications, documents, images
- Publish → public URL + QR PNG; public passport page; scan tracking (`?src=qr`)
- Dashboard + analytics; admin user CRUD

### Bonuses / hardening
- Soft delete + Undo; search + pagination
- Audit log + admin UI
- Drag-and-drop uploads
- Passport versioning + PDF export (BackgroundTasks cache)
- Redis cache (optional); MinIO storage (optional)
- Purge job for expired soft-deleted products
- Rate limiting; refresh-token reuse detection; upload validation

## 5. Security (how we test it)

| Check | Automated | Manual demo |
|-------|-----------|-------------|
| Rate limit on login | `test_rate_limit` | Spam login → `429` + `Retry-After` |
| Refresh reuse | `test_refresh_reuse_*` | Refresh, replay old cookie → sessions die |
| Upload magic/size | unit storage/upload tests | Spoofed `.pdf` / oversized file → `400` |
| Storage key scope | unit storage tests | Cross-product key rejected |
| Roles | users/audit integration tests | Editor → `/users` = `403` |
| Public vs private | passport/products tests | No token on `/products` = `401` |

Access tokens stay in memory on the client (not `localStorage`). Refresh is httpOnly.

## 6. Load / stress

### Seed bulk data

```bash
cd backend
APP_ENV=local uv run python -m scripts.seed_load --count 1000
# optional: publish a sample for public passport hits
APP_ENV=local uv run python -m scripts.seed_load --count 200 --publish-every 20
```

### Run stress (API must be up)

For throughput numbers, temporarily disable rate limits:

```bash
# in backend/.env.local
RATE_LIMIT_ENABLED=false
```

```bash
# API must already be running in another terminal
cd backend
APP_ENV=local uv run python -m scripts.stress_test
# defaults are laptop-safe (8 workers, 80 requests)
```

Results are prepended to [`load-results.md`](./load-results.md).

**What we measure:** overall req/s, per-endpoint OK/error counts, p50/p95/max latency for product list, dashboard, and public passport.

### Representative run (this repo)

Against ~1k `LOAD-*` products, single-process uvicorn, rate limits **off**:

| Setting | Value |
|---------|--------|
| Workers / requests | 20 / 500 |
| Throughput | ~106 req/s |
| Status codes | all `200` |
| Mean latency | ~187 ms |
| p95 (list / dashboard / passport) | ~280 / ~259 / ~259 ms |

With rate limits **on**, the same shape quickly returns `429` (expected). A smaller warm-up (8 / 80) sat around ~111 req/s with ~70 ms mean latency.

## 7. How to run (reviewers)

```bash
cp .env.example .env
cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local

docker compose up db
```

```bash
# API
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
# Web
cd frontend
npm i
npm run dev
```

| | |
|--|--|
| App | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Admin | `admin@example.com` / `admin1234` |
| Editor | `editor@example.com` / `editor1234` |

Production-style API process (Docker / deploy):

```text
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:$PORT app.main:app
```

## 8. Tests & CI

```bash
cd backend && APP_ENV=local uv run pytest
cd frontend && npm test && npm run build
```

GitHub Actions on `main` / PRs runs backend pytest (Postgres service) and frontend unit tests + build.

## 9. Demo walkthrough (5–7 min)

1. Login as admin → Dashboard / Analytics  
2. Products → `DEMO-001` → publish panel (versions, QR, republish)  
3. Soft-delete → Undo; open Audit  
4. Public passport → Download PDF; open with `?src=qr`  
5. Login as editor → Users / Audit hidden  

## 10. What we deliberately skipped

- Full Celery stack (BackgroundTasks is enough for PDF cache)
- Per-user product tenancy (shared back office by design)
- Heavy observability (Prometheus/ELK) — stdout logs + request id instead

---

More detail: [`ARCHITECTURE.md`](./ARCHITECTURE.md) · DB notes: [`../backend/docs/database.md`](../backend/docs/database.md)
