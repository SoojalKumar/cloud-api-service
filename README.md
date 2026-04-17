# Cloud-Based API Service

Cloud-Based API Service is a production-style FastAPI backend scaffold designed to grow into a larger cloud application over time. The project is being built incrementally with small, meaningful commits so the architecture stays clean as the service expands.

## Current Scope

- FastAPI application bootstrap
- Versioned API routes under `/api/v1`
- Typed response models using Pydantic
- Health and service metadata endpoints
- Centralized runtime settings
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

## Available Endpoints

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

Service info:

```text
GET http://127.0.0.1:8000/api/v1/info
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

Example service info response:

```json
{
  "name": "Cloud-Based API Service",
  "version": "0.1.0",
  "environment": "development",
  "docs_url": "/docs"
}
```

## Environment Variables

You can customize the app metadata without changing code:

```bash
export APP_NAME="Cloud-Based API Service"
export APP_VERSION="0.1.0"
export APP_ENV="development"
```
