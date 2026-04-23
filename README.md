# Cloud-Based API Service

Cloud-Based API Service is a production-style FastAPI backend scaffold designed to grow into a larger cloud application over time. The project is being built incrementally with small, meaningful commits so the architecture stays clean as the service expands.

## Current Scope

- FastAPI application bootstrap
- Versioned API routes under `/api/v1`
- Typed response models using Pydantic
- Health and service metadata endpoints
- Task CRUD resource with SQLite persistence, status filtering, pagination, and summary metrics
- Request ID middleware for traceability
- Baseline security headers on API responses
- Consistent JSON error responses
- Centralized runtime settings with configurable CORS origins, database path, and API key
- GitHub Actions test workflow
- Docker-ready runtime setup
- Clean package layout for routes, services, and models

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

Root service metadata:

```text
GET http://127.0.0.1:8000/
```

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
  "environment": "development"
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

Clients can send `X-Request-ID`; otherwise the API generates one and returns it in the response headers. Responses also include baseline browser security headers such as `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.

## Run Tests

Run the automated endpoint tests:

```bash
python -m pytest
```

Current coverage includes:

- `GET /api/v1/health`
- `GET /`
- `GET /api/v1/info`
- SQLite task repository persistence and task service behavior
- task create/list/filter/paginate/summary/update/delete behavior
- standardized 404 and validation error responses
- request ID and security response headers
- environment parsing for deploy-time settings

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
export CORS_ALLOWED_ORIGINS="http://localhost:3000,https://example.com"
```

## Docker

Build and run the API in a container:

```bash
docker build -t cloud-api-service .
docker run -p 8000:8000 cloud-api-service
```

Then verify the service:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Automated Checks

GitHub Actions runs the pytest suite on every push and pull request to `main`, helping keep new API changes safe as the service grows.

## Development Notes

See [docs/development.md](docs/development.md) for local workflow, commit guidelines, and current development priorities.
