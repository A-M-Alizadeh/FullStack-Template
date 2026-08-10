# Deploy (Vercel + Render)

Target shape for a live demo:

| Piece | Host | Notes |
|-------|------|--------|
| Frontend | **Vercel** | Root directory = `frontend` |
| API | **Render** (Docker) | Blueprint: [`render.yaml`](../render.yaml) |
| Database | **Render Postgres** | Wired via `DATABASE_URL` |

Cross-origin auth uses `COOKIE_SECURE=true` + `COOKIE_SAMESITE=none` and CORS credentials. The frontend origin and API URL must match what you configure below.

---

## 1. Backend (Render)

1. Push `master` (includes `render.yaml`).
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → select this repo / `master`.
3. Apply the blueprint (`dpp-db` + `dpp-api`).
4. Wait until the web service is live. Note the API URL, e.g. `https://dpp-api.onrender.com`.
5. Health check: `GET https://<api-host>/api/v1/health` → `{"status":"ok"}` (or equivalent).

Migrations run on container start (`docker-entrypoint.sh` → `alembic upgrade head`).

### Seed demo data (once)

From the Render service **Shell**:

```bash
APP_ENV=production python -m scripts.seed_users
APP_ENV=production python -m scripts.seed_lookups
APP_ENV=production python -m scripts.seed_products
APP_ENV=production python -m scripts.seed_scans
APP_ENV=production python -m scripts.seed_audit
```

Demo logins: `admin@example.com` / `admin1234`, `editor@example.com` / `editor1234`.

---

## 2. Frontend (Vercel)

1. [Vercel](https://vercel.com) → **Add New Project** → import this repo.
2. **Root Directory:** `frontend`
3. Framework: Next.js (see `frontend/vercel.json`)
4. Environment variables:

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://<your-api-host>/api/v1` |
| `NEXT_PUBLIC_APP_NAME` | `Digital Product Passport` |

5. Deploy. Note the site URL, e.g. `https://your-app.vercel.app`.

---

## 3. Wire CORS + cookies (required)

Back on Render → `dpp-api` → **Environment**, set:

| Name | Value |
|------|--------|
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` |

No trailing slash. Redeploy the API. Login from the Vercel site should set the httpOnly refresh cookie on the API host.

---

## 4. Checklist

- [ ] `/api/v1/health` OK on Render  
- [ ] Seeds run once  
- [ ] Vercel build has correct `NEXT_PUBLIC_API_URL`  
- [ ] `CORS_ORIGINS` / `FRONTEND_URL` match the Vercel origin  
- [ ] Login works; soft-refresh keeps session  
- [ ] Public passport + PDF open  

---

## Caveats (demo)

- **`STORAGE_BACKEND=local`** on Render is ephemeral — uploads/QR files can disappear on redeploy. Fine for assessment; use MinIO/S3 for real persistence.
- Free Render web services **spin down** when idle — first request after idle can take ~30–60s.
- Render Postgres uses a small paid plan in `render.yaml` (`basic-256mb`). Free web dynos still spin down when idle.

---

## Local production-compose (optional)

```bash
cp backend/.env.production.example backend/.env.production
cp frontend/.env.production.example frontend/.env.production
# edit secrets + URLs, then:
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

See also [`backend/.env.production.example`](../backend/.env.production.example).
