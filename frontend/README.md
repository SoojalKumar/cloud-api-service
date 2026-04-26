# Frontend — Cloud-Based API Service

A small React + Vite + TypeScript demo UI for the FastAPI backend in `../app`.
The goal is a thin, recruiter-friendly surface over the existing API — not a
production application. It deliberately avoids heavy dependencies (no state
library, no UI kit, no test runner yet) so the backend stays the centerpiece.

![Demo UI screenshot](screenshot.png)

## What it does

- Lists tasks from `GET /api/v1/tasks` with status filtering.
- Shows aggregate counts from `GET /api/v1/tasks/summary`.
- Creates, advances, and deletes tasks via authenticated writes.
- Surfaces backend `request_id` in error banners so the UI ties back to server logs.

## Run locally

The frontend assumes the FastAPI backend is running on `http://localhost:8000`
(see the root `README.md`). Vite proxies all `/api/*` calls to that backend, so
there is no CORS dance during development.

```bash
cd frontend
bun install        # uses the committed bun.lock for reproducibility
bun run dev
```

`bun` is the preferred package manager because the only committed lockfile is
`bun.lock`. `npm install` works as a fallback but will resolve fresh versions
within the `^` ranges in `package.json` and may drift from what was tested. If
you commit a `package-lock.json`, prefer `npm` to keep one source of truth.

Open <http://localhost:5173>. Paste your `API_KEY` (from `.env` or
`development-api-key` by default) into the API key field — it is stored in
`localStorage` only and is required for create / update / delete actions.

If your backend runs on a different host, point the dev proxy at it:

```bash
VITE_BACKEND_URL=http://192.168.1.5:8000 bun run dev
```

## Build

```bash
bun run build       # type-checks then builds to dist/
bun run preview     # serve the production build locally
```

For a deployed build, set the API base URL at build time:

```bash
VITE_API_BASE_URL=https://api.example.com bun run build
```

When `VITE_API_BASE_URL` is unset, the build calls relative `/api/*` paths,
which works when the frontend and backend share an origin.

## Why hand-written types?

The API surface is four routes. Hand-maintaining a 30-line `types.ts` and a
~120-line `api.ts` is cheaper than wiring up `openapi-typescript`, the
generation script, and a CI drift check for so few endpoints. If the API grows
past ~10 routes, switch to schema generation.

## Why no test runner?

This is an MVP demo. Adding Vitest + React Testing Library + MSW would more than
double the file count for what is currently a 2-component app. The backend has
full test coverage; the frontend's correctness is verified by hand against the
running API. Add tests when the surface stabilizes.
