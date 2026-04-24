# Architecture

This document describes how the Cloud-Based API Service is organized so new contributors can onboard quickly and reviewers can reason about each change in isolation.

## Design Goals

- **Small, reviewable commits.** Each behavior lives in its own module so history stays readable.
- **Clear layering.** Routes handle HTTP, services enforce business rules, repositories own persistence.
- **Production-style defaults.** Request tracing, security headers, standardized errors, and configuration validation all ship by default.
- **Easy local ergonomics.** A `Makefile`, management CLI, and `.env.example` keep local setup consistent.

## Module Layout

```text
app/
  main.py              # FastAPI app wiring, middleware, exception handlers
  config.py            # Environment loading, validation, Settings dataclass
  runtime.py           # Process-wide runtime metadata (uptime)
  logging.py           # Logging configuration
  security.py          # API key dependency for protected routes
  database.py          # SQLite connection helper + readiness probe
  migrations.py        # Versioned schema migrations applied on startup
  cli.py               # Management commands (migrate, seed-demo, reset-db, show-config)
  errors.py            # AppError hierarchy + FastAPI exception handlers
  middleware/
    request_id.py       # Assigns/propagates X-Request-ID
    access_log.py       # Logs method/path/status + X-Process-Time header
    security_headers.py # Sets baseline browser security headers
  models/
    system.py           # Health and service-info response contracts
    tasks.py            # Task request/response/status models
    errors.py           # Standard error response contract
  routes/
    root.py             # GET /
    system.py           # GET /api/v1/health, /api/v1/info
    tasks.py            # Task CRUD + summary endpoints
  services/
    health.py           # Builds health payload, checks DB readiness, uptime
    system.py           # Builds service-info payload
    tasks.py            # Task business rules on top of the repository
  repositories/
    tasks.py            # SQLite-backed task persistence
tests/                 # Endpoint, service, repository, CLI, config tests
docs/
  development.md       # Local workflow and contribution guidance
  operations.md        # Make/CLI commands, deployment notes
  architecture.md      # This document
```

## Request Lifecycle

1. **Client** calls an endpoint with an optional `X-Request-ID` header.
2. `RequestIdMiddleware` attaches (or generates) the request ID on `request.state`.
3. `AccessLogMiddleware` records a timed access-log line and sets `X-Process-Time` on the response.
4. `SecurityHeadersMiddleware` attaches baseline headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`).
5. `CORSMiddleware` applies the configured `CORS_ALLOWED_ORIGINS`.
6. FastAPI routes protected mutations through `Depends(require_api_key)`.
7. Route handlers call service methods that validate input and delegate to repositories for persistence.
8. Errors raised as `AppError` subclasses, `StarletteHTTPException`, or `RequestValidationError` are all normalized by handlers in `app/errors.py` to a consistent JSON payload that includes the request ID.

## Data Flow for Tasks

```text
POST /api/v1/tasks
  ├── require_api_key            (security.py)
  ├── TaskCreate validation      (models/tasks.py)
  ├── TaskService.create_task    (services/tasks.py)
  └── SQLiteTaskRepository.create (repositories/tasks.py)
         └── INSERT INTO tasks   (SQLite)
```

Reads follow the inverse path. `TaskService.get_task` raises `ResourceNotFoundError` when the repository returns `None`, which is rendered as a standardized 404 payload.

## Configuration

`app/config.py` loads environment variables, optionally from a local `.env`, validates bounded values (`APP_ENV`, `LOG_LEVEL`), rejects empty required values, and exposes a frozen `Settings` dataclass consumed across the app. `.env.example` documents every supported variable.

## Persistence and Migrations

`SQLiteTaskRepository` is the only component that speaks SQL. It opens a SQLite connection, runs `apply_migrations`, and executes parameterized queries. Schema changes are modeled as new entries in `MIGRATIONS` in `app/migrations.py`, recorded in `schema_migrations`, and applied at startup (or on demand through `python -m app.cli migrate`).

## Error Contract

All API errors return the shape:

```json
{
  "error": "not_found",
  "message": "Task '...' was not found.",
  "request_id": "abc-123"
}
```

The `error` slug is stable and safe for clients to match on. The `message` is human-readable. The `request_id` ties the client's complaint to server logs.

## Extending the Service

- **New resource:** add a Pydantic model, a repository, a service, and routes; register the router in `app/main.py`.
- **New config key:** extend `Settings` with a validated loader, document in `.env.example` and `README.md`.
- **New migration:** append a `Migration` to `MIGRATIONS`; the migration runner is idempotent.
- **New middleware:** add a module under `app/middleware/` and register it in `app/main.py`.

Keeping these extension points obvious is why the layering is enforced: nothing outside `repositories/` touches SQL, and nothing outside `routes/` knows about HTTP.
