# Cloud-Based API Service

Cloud-Based API Service is a production-style FastAPI backend scaffold designed to grow into a larger cloud application over time. The project starts with a clean service-oriented layout and a health endpoint, with future features intended to be added through small, meaningful commits.

## Current Scope

- FastAPI application bootstrap
- Health check endpoint
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

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "ok"}
```
