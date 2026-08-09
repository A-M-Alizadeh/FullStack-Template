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
    passports/
    analytics/
    users/                # admin only (RoleGate)
    settings/
  passport/[uuid]/       # public passport (no auth)
components/               # shell, AuthGate, RoleGate, feedback
features/                 # domain UI
store/
  api/                    # RTK Query endpoints
  auth/                   # access token + user (memory only)
lib/                      # env, errors, i18n, navigation
hooks/
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

## Auth & roles

- Refresh token: httpOnly cookie (`credentials: "include"`)
- Access token: in-memory RTK slice; `Authorization: Bearer …`
- Reload → `/auth/refresh` via cookie → new access
- Nav items can set `roles` (e.g. Users = admin)
- Pages use `RoleGate` where needed; API still enforces roles

## Shipped

| Area | Notes |
|------|--------|
| Login / session | RHF + Zod; AuthGate bootstrap |
| Products | CRUD + nested tabs; list cover / QR modal / views |
| Publish + QR | Editor panel + QR dialog |
| Preview tab | Iframe of public passport after publish |
| Passports | Published products list |
| Users | Admin CRUD (hidden from editors) |
| Dashboard / analytics | Summaries and scan tables |
| Public passport | Brand mark; `?src=qr` scan tracking |
| Settings | Light/dark + EN/IT (`useT`) |

## Tests

```bash
npm test              # Vitest (unit + RTL)
npm run test:watch
```

E2E smoke (API + DB must be up with seed users):

```bash
npx playwright install chromium   # once
npm run test:e2e
npm run test:e2e:headed
npm run test:e2e:ui
```
