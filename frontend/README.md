# Frontend

Next.js (App Router) + TypeScript + MUI + Redux Toolkit / RTK Query.

Talks to the FastAPI backend directly (no Next.js API routes for business logic).

## Layout

```
app/
  (auth)/login/           # guest-only login
  (backoffice)/           # AuthGate + AppShell
    dashboard/
    products/             # list, new, [id]
    analytics/
  passport/[uuid]/       # public passport (no auth)
components/               # shell, auth gates, shared feedback
features/                 # domain UI (auth, products, dashboard, …)
store/
  api/                    # RTK Query (auth, products, dashboard, analytics, passport)
  auth/                   # access token + user (memory only)
lib/                      # env, errors, i18n, helpers
hooks/                    # useAuthBootstrap, useT
theme/
types/
```

## Run

```bash
cp .env.local.example .env.local
npm i
npm run dev
```

App: http://localhost:3000 — API must be up on :8000 (`NEXT_PUBLIC_API_URL`).

## Auth

- Refresh token: httpOnly cookie from FastAPI (`credentials: "include"`)
- Access token: in-memory RTK slice; `Authorization: Bearer …`
- Reload → `/auth/refresh` via cookie → new access

## Shipped

| Area | Notes |
|------|--------|
| Login / session | RHF + Zod; AuthGate bootstrap |
| Products | CRUD + nested tabs (materials, sustainability, certs, docs, images) |
| Publish + QR | Panel on product editor; download PNG |
| Dashboard / analytics | Read-only summaries and scan tables |
| Public passport | `/passport/{uuid}`; forwards `?src=qr` (no remount refetch) |
| Settings | Light/dark theme + EN/IT language (localStorage); `useT` |

## Tests

```bash
npm test          # Vitest (lib + Zod schemas)
npm run test:watch
```

| Layer | What | Status |
|-------|------|--------|
| `lib/` + Zod schemas | Unit (Vitest) | Done |
| Components | RTL (Login, Settings) | Done |
| E2E smoke | Playwright | Planned |
