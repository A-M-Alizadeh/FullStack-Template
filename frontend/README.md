# Frontend

Next.js (App Router) + TypeScript + MUI + Redux Toolkit / RTK Query.

Talks to the FastAPI backend. No Next.js API routes for business logic (call FastAPI directly).

## Target layout

```
app/                    # routes only (App Router)
  (auth)/               # login (no app chrome)
  (backoffice)/         # dashboard, products, … (shared shell)
  passport/[uuid]/     # public passport
components/             # shared UI (layout, feedback, form bits)
features/               # domain UI pieces if a page grows (optional early)
store/
  index.ts              # configureStore
  hooks.ts              # typed useAppDispatch / useAppSelector
  StoreProvider.tsx
  auth/authSlice.ts     # access token + user (memory only)
  api/
    baseQuery.ts        # fetch + cookie credentials + 401 refresh
    baseApi.ts          # createApi shell
    authApi.ts          # login / refresh / logout / me
theme/                  # MUI theme
types/                  # shared TS types (auth, …)
lib/                    # small helpers (env, paths)
public/                 # static files (favicon, …)
hooks/                  # shared hooks
```

Expand by adding: `store/api/<domain>.ts`, a route under `app/`, and components under `components/` or `features/<domain>/`.

## Testability

Keep logic out of pages/components so it stays easy to unit-test later:

| Layer | What goes here | Test style |
|-------|----------------|------------|
| `lib/` | Pure helpers (env, formatters, mappers) | Unit, no React |
| `store/` / `store/api/` | Auth state, RTK Query endpoints, transforms | Unit / MSW |
| `hooks/` | Reusable behavior | React Testing Library |
| `components/` / `features/` | UI only — call hooks/store, little business logic | RTL |
| `app/` | Routing + composition only | Light / e2e |

Rule: if it isn’t rendering UI, it shouldn’t live in a `page.tsx`.

## Env

```bash
cp .env.local.example .env.local
```

- `NEXT_PUBLIC_API_URL` — backend API prefix (e.g. `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_APP_NAME` — app title

## Run

```bash
npm i
npm run dev
```

App: http://localhost:3000 — API must be up on :8000.

## Auth model (with backend)

- Refresh token: httpOnly cookie (set by FastAPI)
- Access token: in memory only (RTK auth slice); `Authorization: Bearer …`
- Requests use `credentials: "include"`
- Reload → `/auth/refresh` via cookie → new access in memory

Backend cookie support is a small step before frontend auth UI (see steps below).

## Steps

### 0. Backend: httpOnly refresh cookie (short)

Login/refresh/logout set or clear refresh cookie; CORS `allow_credentials`; access still Bearer. Keep tests green.

### 1. Folders + config + theme

Create the layout above. Wire env helper, MUI theme in `theme/`, `AppProviders` (theme + later Redux). No real pages yet.

### 2. RTK store + API layer

- `store/index.ts` — configureStore
- `store/api/baseApi.ts` — fetchBaseQuery → FastAPI, credentials, Bearer from auth state, 401 → refresh once
- Empty endpoint modules ready to grow (`authApi`, `productsApi`, …)
- `store/authSlice.ts` — access token + user in memory

### 3. App shell + routing

Route groups: `(auth)`, `(backoffice)`, public `passport/[uuid]`. Back-office layout (nav). Auth gate: redirect to login if no access (and refresh failed).

### 4. Login + session

Login form → set cookie (backend) + store access/user. Logout clears cookie + memory. `/me` on bootstrap when access exists.

### 5. Products

List / create / edit + nested sections (materials, sustainability, certs, docs, images) via RTK Query. Loading skeletons, basic Zod/RHF validation.

### 6. Publish + QR

Publish action, show QR / download from API.

### 7. Dashboard + analytics

Read-only pages on back-office nav.

### 8. Public passport

`/passport/[uuid]` — no auth; forward `?src=qr` to API.

### 9. Polish

Empty/error states, small i18n hook point (optional), README sync.

## Done so far

0. Next.js + MUI stub scaffold.
0. Backend httpOnly refresh cookie (on `feat/frontend`).
1. Folders (`lib`, `theme`, `types`, `hooks`, `features`) + env helper + MUI theme + providers.
2. RTK store + `baseQuery` (credentials + reauth) + `authApi` + memory auth slice.
3. Routes `(auth)` / `(backoffice)` / `passport/[uuid]`, AppShell, AuthGate (`lib/authSession` bootstrap).
4. Login form (RHF + Zod) → access cookie session + `/me` → dashboard.
5. Products list / create / edit + nested (materials, sustainability, certs, docs, images).
6. Publish + QR (panel on product editor; download PNG).
7. Dashboard + analytics (read-only RTK pages).
8. Public passport (`/passport/[uuid]`, forwards `?src=qr`; no remount refetch).

## Next

9. Polish (empty/error states, README sync).
