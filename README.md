# Cloud-Based API Service

[![Tests](https://github.com/SoojalKumar/cloud-api-service/actions/workflows/tests.yml/badge.svg)](https://github.com/SoojalKumar/cloud-api-service/actions/workflows/tests.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/license-MIT-informational.svg)](LICENSE)

Cloud-Based API Service is a production-style FastAPI backend built incrementally with small, reviewable commits. It ships with typed endpoints, SQLite persistence, versioned migrations, API key authentication, request tracing, standardized error responses, a management CLI, a multi-stage Docker image that bundles a React demo UI on the same origin, and a GitHub Actions pipeline that runs the test suite and builds the frontend on every push.

## Live Demo

A hosted copy of the full app (API + React UI served from one image) lives on Hugging Face Spaces:

> **Demo:** `https://<your-hf-username>-cloud-api-service.hf.space` *(set up once; see [Deployment](#deployment))*

Paste the default write key `development-api-key` into the UI to create, advance, or delete tasks. OpenAPI docs are on `/docs` and the health probe is `/api/v1/health` on the same host. The free Spaces tier uses an ephemeral filesystem, so each cold boot re-seeds three demo tasks — every visitor gets a working app, not an empty one.

## Project Status

The core service is feature-complete for a portfolio backend:

- End-to-end API for a real resource (`tasks`) with validation, pagination, and filtering.
- Persistence layer with versioned migrations and a readiness probe.
- Authenticated mutations, consistent error payloads, security headers, request IDs, access logging, and uptime reporting.
- Full test suite wired to CI, plus Make/CLI ergonomics for local work.

See [docs/architecture.md](docs/architecture.md) for module layout and request flow.

## Current Scope

- FastAPI application bootstrap via a `create_app()` factory for testability
- Versioned API routes under `/api/v1`
- Typed response models using Pydantic
- Health and service metadata endpoints with database readiness and process uptime
- Task CRUD resource with SQLite persistence, status filtering, pagination, and aggregate summary metrics (single `GROUP BY` query, exact at any scale)
- Request ID middleware for traceability
- Baseline security headers on API responses
- Consistent JSON error responses, with field-level detail on validation errors
- Centralized runtime settings with configurable CORS origins, database path, and API key
- GitHub Actions workflows: pytest suite + frontend type-check and production build on every push
- Project CLI for migrations, demo seeding, reset, and config inspection
- Makefile shortcuts for common local operations
- Multi-stage Docker image: bundles the Vite-built React UI into the same Python runtime image and serves it on `/` — one origin, no CORS dance in production
- Clean package layout for routes, services, and models
- React + Vite + TypeScript demo UI in `frontend/` with a defensive fetch client (tolerates non-JSON error bodies and HTML edge-case responses)

## Run The Server

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Available Endpoints

Root (`/`) behavior depends on whether a built frontend is present:

- If `frontend/dist/index.html` exists (set via `FRONTEND_DIST_DIR` or default path), the Vite-built React UI is served at `/`. This is what the production Docker image does.
- Otherwise (dev without a build), `/` returns JSON service metadata so `curl` and tests keep working.

The canonical JSON metadata endpoint is always at `/api/v1/info`, regardless of whether the frontend is mounted.

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

Service info:

```text
GET http://127.0.0.1:8000/api/v1/info
```

Task resource:

```text
POST   http://127.0.0.1:8000/api/v1/tasks  (requires X-API-Key)
GET    http://127.0.0.1:8000/api/v1/tasks
GET    http://127.0.0.1:8000/api/v1/tasks?status=in_progress&offset=0&limit=25
GET    http://127.0.0.1:8000/api/v1/tasks/summary
GET    http://127.0.0.1:8000/api/v1/tasks/{task_id}
PATCH  http://127.0.0.1:8000/api/v1/tasks/{task_id}  (requires X-API-Key)
DELETE http://127.0.0.1:8000/api/v1/tasks/{task_id}  (requires X-API-Key)
```

Example health response:

```json
{
  "status": "ok",
  "service": "Cloud-Based API Service",
  "version": "0.1.0",
  "environment": "development",
  "database": "ok",
  "uptime_seconds": 12.438
}
```

Example task creation:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-api-key" \
  -d '{"title":"Prepare deployment plan","description":"Document next production steps."}'
```

Example task summary response:

```json
{
  "total": 3,
  "todo": 1,
  "in_progress": 1,
  "done": 1
}
```

Example service info response:

```json
{
  "name": "Cloud-Based API Service",
  "version": "0.1.0",
  "environment": "development",
  "docs_url": "/docs",
  "auth_mode": "api_key",
  "persistence": "sqlite"
}
```

## Authentication

Write operations on `/api/v1/tasks` are protected by a shared API key. Send the `X-API-Key` header with the value from `API_KEY` when creating, updating, or deleting tasks. Read-only task endpoints remain public for now.

## Persistence

Tasks are stored in SQLite through a repository layer. By default, the API uses `cloud_api_service.db` in the project root. For deployments or tests, set `DATABASE_PATH` to point at a different SQLite database file.

## Error Responses

All API errors use a consistent JSON response shape and include a request ID when available:

```json
{
  "error": "not_found",
  "message": "Not Found",
  "request_id": "test-request-1"
}
```

Validation errors (HTTP 422) additionally include a `fields` array so clients can point the user at the exact input that failed, without reading server logs:

```json
{
  "error": "validation_error",
  "message": "Request validation failed.",
  "request_id": "req-abc",
  "fields": [
    { "field": "body.title", "message": "Field required", "type": "missing" }
  ]
}
```

Clients can send `X-Request-ID`; otherwise the API generates one and returns it in the response headers. Responses also include baseline browser security headers such as `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.

## Run Tests

Run the automated endpoint tests:

```bash
python -m pytest
# or
make test
```

Current coverage (34 tests) includes:

- `GET /api/v1/health` and `GET /api/v1/info`
- Root (`/`) behavior in both modes: JSON metadata when no frontend is built, and static HTML when `frontend/dist/` is present
- SQLite task repository persistence and task service behavior
- Task create/list/filter/paginate/summary/update/delete behavior
- `GET /tasks/summary` correctness beyond 1500 rows (regression test for a bug where the summary was capped at 1000 in-memory)
- Standardized 404, validation, and authentication error responses
- Validation errors include a `fields` array pointing at the failing input
- Request ID and security response headers
- Environment parsing for deploy-time settings

## Environment Variables

You can customize app metadata and CORS behavior without changing code. Start by copying the example file:

```bash
cp .env.example .env
```

Then export values in your shell or load them through your deployment platform:

```bash
export APP_NAME="Cloud-Based API Service"
export APP_VERSION="0.1.0"
export APP_ENV="development"
export DATABASE_PATH="cloud_api_service.db"
export API_KEY="development-api-key"
export CORS_ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"
```

## Local Operations

The project includes a small management CLI and `Makefile` shortcuts for common workflows:

```bash
make migrate
make seed-demo
make run
make show-config
```

Direct CLI usage is also available:

```bash
python -m app.cli migrate
python -m app.cli seed-demo
```

## Demo Frontend

A small React + Vite + TypeScript UI lives in [`frontend/`](frontend/) and talks to the API through Vite's dev proxy, so there is no CORS dance during local development.

![Demo UI screenshot](frontend/screenshot.png)

```bash
cd frontend
bun install        # uses the committed bun.lock; npm works as a fallback
bun run dev
```

Open <http://localhost:5173>, paste your `API_KEY` (default `development-api-key`) into the API key field, and create / advance / delete tasks against the running backend on `:8000`. See [`frontend/README.md`](frontend/README.md) for the design rationale, package-manager note, and build instructions.

## Docker

The `Dockerfile` is multi-stage: the first stage builds the React frontend with Bun, the second stage installs Python dependencies, copies the built `dist/` into the image, and runs as a non-root `appuser`. The final image serves both the API and the UI on port 8000 from a single origin.

```bash
docker build -t cloud-api-service .
docker run -p 8000:8000 cloud-api-service
```

Then verify the service:

```bash
curl http://127.0.0.1:8000/api/v1/health
open http://127.0.0.1:8000/            # React dashboard
open http://127.0.0.1:8000/docs        # OpenAPI / Swagger
```

The container boots by running `app.cli migrate` and then `app.cli seed-demo` before starting `uvicorn`, so a fresh deploy (or a fresh ephemeral volume on free hosting tiers) always boots into a working UI with three demo tasks. Override the SQLite path with `DATABASE_PATH` if you mount a persistent volume.

## Deployment

The project is set up to deploy to three hosts without code changes — pick the one that matches your cost/uptime preferences:

### Hugging Face Spaces (free, always-on, no credit card)

The `deploy-hf-space` workflow in `.github/workflows/` pushes the repo to a Hugging Face Space on every push to `main`, swapping in an HF-specific README (`.github/hf_space_readme.md`) that carries the required YAML front-matter.

One-time setup:

1. Create a Hugging Face account and a new **Docker** Space named `cloud-api-service`.
2. Generate a "write" token at <https://huggingface.co/settings/tokens>.
3. In the GitHub repo settings, add two **Actions secrets**: `HF_USERNAME` (your HF account name) and `HF_TOKEN` (the write token).

Push to `main`; the workflow force-pushes the repo into the Space and HF Spaces rebuilds the container. Live URL pattern: `https://<HF_USERNAME>-cloud-api-service.hf.space`.

Note: the free Spaces filesystem is ephemeral, so SQLite resets on every container restart. The `seed-demo` step in the Dockerfile recreates three demo tasks on each boot, which is the right behavior for a stateless demo.

### Fly.io (pay-as-you-go; ~$0 on `auto_stop_machines = "stop"` with the $5 trial credit)

`fly.toml` is already authored with a 256MB shared-cpu-1x VM in `iad`, a 1GB persistent volume mounted at `/app/data`, and a `/api/v1/health` HTTP check.

```bash
flyctl auth login
flyctl apps create cloud-api-service           # rename if the slug is taken
flyctl volumes create cloud_api_service_data --region iad --size 1 -y
flyctl deploy --remote-only
```

Set production secrets (don't rely on the dev default key for a public deploy):

```bash
flyctl secrets set API_KEY="$(openssl rand -hex 24)"
```

### Any other Docker host

The image is vanilla. If your host speaks `docker run`, it speaks this app. Persist `/app/data` for SQLite durability (or use `DATABASE_PATH` to point at a managed database).

## Automated Checks

GitHub Actions runs two parallel jobs on every push and PR to `main`:

- **Run pytest** — installs the Python deps and executes the full backend test suite.
- **Build frontend** — installs the frozen Bun lockfile, type-checks the TypeScript, and produces a production Vite build. This catches frontend regressions before they can break a deploy.

A separate `Deploy to Hugging Face Space` workflow triggers on the same pushes but no-ops gracefully when the `HF_TOKEN` / `HF_USERNAME` secrets are not configured.

## Development Notes

- [docs/architecture.md](docs/architecture.md) — module layout, request lifecycle, extension points.
- [docs/development.md](docs/development.md) — local workflow, commit guidelines, current priorities.
- [docs/operations.md](docs/operations.md) — Make/CLI commands, database lifecycle, deployment notes.
