# Frontend

Next.js (App Router) + TypeScript + MUI + RTK Query.

Talks to FastAPI directly (no Next.js business API routes).

Report: [`../docs/REPORT.md`](../docs/REPORT.md)

## Run

```bash
cp .env.local.example .env.local
npm i
npm run dev
```

App: http://localhost:3000 — API on :8000 (`NEXT_PUBLIC_API_URL`).

## Auth

- Refresh: httpOnly cookie (`credentials: "include"`)
- Access: in-memory Bearer token (not `localStorage`)
- `RoleGate` + nav roles; API still enforces authorization

## Main screens

Dashboard, Products (search/pagination, Undo delete), Passports, Analytics, Audit (admin), Users (admin), Settings (theme/i18n), public `/passport/[uuid]` with PDF download.

## Tests

```bash
npm test
npm run build
```

E2E (API + seeds running):

```bash
npx playwright install chromium   # once
npm run test:e2e
```

CI runs unit tests + production build on `main`/`master`.
