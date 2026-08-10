# Frontend

Next.js (App Router) + TypeScript + MUI + RTK Query.

Talks to FastAPI directly (no Next.js business API routes).

## Layout

```
app/
  (auth)/login/
  (backoffice)/          # AuthGate + AppShell
    dashboard/
    products/
    passports/
    analytics/
    audit/               # admin (RoleGate)
    users/               # admin (RoleGate)
    settings/
  passport/[uuid]/      # public
components/
features/
store/                   # RTK Query + auth slice (access token in memory)
lib/                     # env, i18n, navigation
```

## Run

```bash
cp .env.local.example .env.local
npm i
npm run dev
```

App: http://localhost:3000 — API must be on :8000 (`NEXT_PUBLIC_API_URL`).

## Auth & roles

- Refresh: httpOnly cookie (`credentials: "include"`)
- Access: in-memory Bearer token; reload uses `/auth/refresh`
- Nav `roles` + page `RoleGate`; API remains source of truth

## Features

| Area | Notes |
|------|--------|
| Products | CRUD, nested tabs, search/pagination, cover, QR modal, Undo delete |
| Publish | QR, public link, republish + version history |
| Uploads | Drag-and-drop on certs / docs / images |
| Passports | Published list |
| Public page | Brand mark, PDF download, `?src=qr` tracking |
| Audit / Users | Admin only |
| Settings | Light/dark + EN/IT |

## Tests

```bash
npm test
npm run test:watch
```

E2E (API + seeded DB):

```bash
npx playwright install chromium   # once
npm run test:e2e
```
