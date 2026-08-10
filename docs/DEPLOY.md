# Deploy (free path: Neon + Render + Vercel)

| Piece | Host | Cost |
|-------|------|------|
| Database | **Neon** | Free tier |
| API | **Render** free Docker web service | Free (sleeps when idle) |
| Frontend | **Vercel** | Free hobby |

No Render Postgres → no card required for the DB. Blueprint: [`render.yaml`](../render.yaml).

Cross-origin auth needs `COOKIE_SECURE=true`, `COOKIE_SAMESITE=none`, and matching CORS.

---

## 0. Push latest `master`

Include the free-path `render.yaml` (API only, `DATABASE_URL` set manually).

---

## 1. Neon (Postgres) — create first

1. Sign up: [https://neon.tech](https://neon.tech) (GitHub login is fine).
2. **New project** → name it `dpp` (region close to you / EU if available).
3. Open **Connection details** → copy the URI  
   (`postgresql://...@...neon.tech/neondb?sslmode=require`).
4. Keep that string handy — it becomes Render’s `DATABASE_URL`.

---

## 2. Render (API)

1. [https://dashboard.render.com](https://dashboard.render.com) — sign up with GitHub if needed.
2. **New** → **Blueprint** → this repo / branch `master`.
3. When prompted for `DATABASE_URL`, paste the Neon URI.
4. Apply. Wait for `dpp-api` to go live.
5. Note the URL, e.g. `https://dpp-api.onrender.com`.
6. Check: `https://<api-host>/api/v1/health` → `{"status":"ok"}`.

First boot runs `alembic upgrade head` via `docker-entrypoint.sh`.

If the Blueprint fails because `DATABASE_URL` was empty: open the service → **Environment** → set `DATABASE_URL` → **Manual Deploy**.

### Seed demo data (once)

Render **Shell is not on the free plan**. Seed from your laptop against Neon instead
(same `DATABASE_URL`; tables were already created by Alembic on Render boot):

```bash
cd backend
export DATABASE_URL='postgresql://…neon.tech/neondb?sslmode=require'   # your Neon URI
APP_ENV=local uv run python -m scripts.seed_users
APP_ENV=local uv run python -m scripts.seed_lookups
APP_ENV=local uv run python -m scripts.seed_products
APP_ENV=local uv run python -m scripts.seed_scans
APP_ENV=local uv run python -m scripts.seed_audit
```

`DATABASE_URL` overrides local Postgres. Other settings still come from `.env.local`.

| Email | Password |
|-------|----------|
| `admin@example.com` | `admin1234` |
| `editor@example.com` | `editor1234` |

---

## 3. Vercel (frontend only)

Do **not** use Application Preset **Services** (that tries to host FastAPI on Vercel).
The API stays on Render.

1. [https://vercel.com](https://vercel.com) → **Add New Project** → this repo.
2. Change preset away from **Services** if shown — pick a normal **Next.js** / web app import.
3. Set **Root Directory** to `frontend` (Edit → `frontend` → Continue).
4. Framework: Next.js. Ignore / do not add a backend service.
5. Environment variables:

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://<your-render-host>/api/v1` |
| `NEXT_PUBLIC_APP_NAME` | `Digital Product Passport` |

6. Deploy. Copy the site URL (`https://….vercel.app`).

If Vercel keeps forcing “Services”, cancel and use: **Add Project** → same repo →  
**Root Directory = frontend** only (no backend path).

---

## 4. Wire CORS (required)

Render → `dpp-api` → **Environment**:

| Name | Value |
|------|--------|
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` |

No trailing slash. **Save** → **Manual Deploy**. Then try login from the Vercel URL.

---

## 5. Checklist

- [ ] Neon project created; URI in Render `DATABASE_URL`
- [ ] `/api/v1/health` OK (wait ~1 min if the free dyno was asleep)
- [ ] Seeds run once
- [ ] Vercel `NEXT_PUBLIC_API_URL` points at Render
- [ ] CORS / `FRONTEND_URL` match Vercel origin
- [ ] Login works

---

## Caveats

- Free Render **sleeps** — first request after idle can take 30–60s.
- Local disk uploads on Render are **ephemeral** (fine for demo).
- Neon free tier may suspend inactive projects — wake by opening the Neon console or hitting the API.

---

## Accounts to create (order)

1. **Neon** — database  
2. **Render** — API (paste Neon URL)  
3. **Vercel** — frontend (point at Render API)
