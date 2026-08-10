# Architecture — Digital Product Passport (DPP)

Short overview of how the system is built, why key choices were made, and how it can grow.

## 1. System architecture

```
Browser (Next.js)
  ├─ Back office (auth required)  →  FastAPI /api/v1/*   →  PostgreSQL
  │                                    └─ local uploads/
  └─ Public passport /passport/{uuid}
         └─ GET passport (+ optional ?src=qr → qr_scans)
```

| Layer | Tech | Role |
|-------|------|------|
| Frontend | Next.js App Router, TypeScript, MUI, RTK Query | UI only — no business API routes |
| Backend | FastAPI, SQLAlchemy 2, Pydantic v2, Alembic | Auth, domain APIs, file serve |
| Data | PostgreSQL | Users, products, nested resources, passports, scans |
| Files | Local disk or MinIO behind `Storage` protocol | Certs, docs, images, QR PNGs, passport PDFs |

**Local run:** Postgres in Docker; API and Next on the host. Dockerfiles exist for full-stack Compose when needed.

## 2. Design decisions

**Domain modules, thin routers.**  
Routes live under `auth`, `users`, `products`, `passport`, `dashboard`, `analytics`. Routers parse HTTP and call services; services own DB rules and side effects (publish, QR, scans).

**SPA talks to FastAPI directly.**  
Next.js is the UI shell. Keeps one OpenAPI surface (`/docs`) and avoids duplicating auth/validation in Next API routes.

**Passport is a separate table.**  
Publishing creates a `passports` row with a stable `public_uuid` and QR asset. Republish keeps the same UUID/QR, revokes the previous row, and inserts version `N+1`. Public GET serves the active version (optional `?version=` for history).

**Roles are coarse and explicit.**  
`admin` | `editor`. Editors manage products/passports/analytics. Admins also manage users. Enforcement:

1. API: `RequireAdmin` / `RequireEditorOrAdmin`
2. Nav: optional `roles` on nav items
3. Pages: `RoleGate` (e.g. Users = admin only)

UI gates are UX only; the API is the source of truth.

**i18n / theme on the client.**  
EN/IT strings and light/dark mode live in `localStorage` — good enough for a back-office demo without a preferences API.

## 3. Database design

Normalized around **products**:

- Children: materials, sustainability (1:1), certifications, documents, images  
- Lookups: certification types, issuing authorities  
- Publish: `passports` (versioned per product; one `active` row) → append-only `qr_scans`  
- Auth: `users`, `refresh_tokens`  
- Audit: `audit_logs`

Enums cover small fixed sets (role, status, category, doc/image type). Countries are ISO alpha-2 strings validated in code.

Details and ERD: [backend/docs/database.md](../backend/docs/database.md).

Migrations: Alembic (`alembic upgrade head`). Seeds: users, lookups, demo product, scans/versions/PDF, audit samples.

## 4. Security approach

| Concern | Approach |
|---------|----------|
| Passwords | bcrypt hashes; never returned in API |
| Access | Short-lived JWT (`Authorization: Bearer`); role taken from DB on each request |
| Refresh | Opaque token, hashed in DB, **httpOnly** cookie; **rotated** on refresh |
| Refresh theft | Reuse of a rotated refresh token revokes **all** live sessions for that user |
| Rate limits | IP buckets: auth tight, public passport moderate, API default (`429` + `Retry-After`) |
| CORS | Configured origins only (frontend URL) |
| Uploads | Suffix allowlist + magic-byte check + `MAX_UPLOAD_BYTES` |
| Object storage | Keys under `products/{id}/…` only; path traversal rejected; no MinIO listing API |
| Public vs private files | Public media only via passport UUID routes; back-office files need Bearer |
| Authorization | Nested resources scoped by `product_id` + row id (no cross-product IDOR) |
| User admin | Admin only; no self-delete; cannot demote/delete last admin |
| Input | Pydantic v2 on write paths; ORM bound parameters (no string SQL) |

Back-office products are a **shared editor workspace** (any editor/admin may manage products). Isolation is role-based + object-key scoping, not per-user product tenancy.

Access token stays in memory on the client (not `localStorage`) to reduce XSS persistence of long-lived credentials; refresh cookie handles reload.

## 5. Scalability considerations

Current design fits a single-region, moderate-traffic deploy:

- Stateless API processes behind a load balancer (JWT + shared Postgres + shared file store)
- Append-only scan table scales with writes; analytics queries are aggregate/limit, not full history dumps
- List endpoints already accept `skip`/`limit` for paging

Optional infra already wired: MinIO via `STORAGE_BACKEND=minio`, Redis via `REDIS_URL`, PDF export via BackgroundTasks after publish.

## 6. Performance strategies

- Indexed FKs and unique SKU / public UUID  
- Cover image and scan counts enriched in batch on product list (avoid N+1 per row)  
- Public passport loads one graph; QR scan recording is a single insert when `?src=qr`  
- Frontend: RTK Query caching/tags; auth-gated images via blob object URLs  
- Logging to stdout with request id for cheap ops visibility in Docker

## 7. Possible future improvements

Aligned with assessment bonuses / production hardening:

| Area | Idea |
|------|------|
| Soft delete | **Done** — `products.deleted_at`; lists/get hide deleted rows; `POST …/restore` + UI Undo |
| Purge job | **Done** — `scripts.purge_deleted_products` hard-deletes rows past `SOFT_DELETE_RETENTION_DAYS` + files |
| Search / filters | **Done** — `q` + `status` on product list; UI pagination |
| Audit log | **Done** — `audit_logs` table; admin `/audit` UI; create/delete/restore/publish/user mutations |
| Drag & drop uploads | **Done** — shared `FileDropZone` on certs/docs/images |
| Passport versioning | **Done** — republish bumps version, keeps `public_uuid`/QR; revoked history + versions API/UI |
| Object storage | **Done** — `STORAGE_BACKEND=minio` swaps in `MinioStorage` (`Storage` protocol) |
| Export | **Done** — `GET /passport/{uuid}/pdf` (ReportLab); public download button |
| Jobs | **Done** — FastAPI `BackgroundTasks` caches PDF after publish |
| Cache | **Done** — Redis for dashboard/analytics (`REDIS_URL`; NullCache fallback) |

## 8. Testing

| Layer | Tool | Coverage focus |
|-------|------|----------------|
| Backend unit | Pytest | Security helpers, schemas, storage |
| Backend integration | Pytest + `dpp_test` DB | Auth, products, passport, users CRUD/roles, dashboard |
| Frontend unit / RTL | Vitest | Forms, RoleGate/nav, users list |
| E2E | Playwright | Login, products, admin vs editor Users nav |

---

**Summary:** Modular FastAPI + Next.js SPA, normalized Postgres schema with a versioned public passport, JWT + httpOnly refresh, role checks at API / nav / page, plus soft delete, audit, Redis cache, MinIO-ready storage, and PDF export.
