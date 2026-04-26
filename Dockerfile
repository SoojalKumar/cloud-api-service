# --- Stage 1: build the React frontend ----------------------------------------
# Bun is the project's preferred package manager (see frontend/README.md) so the
# committed bun.lock is the reproducible source of truth.
FROM oven/bun:1.3-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile

COPY frontend/ ./
RUN bun run build

# --- Stage 2: Python runtime --------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/cloud_api_service.db

# Create a non-root user. Hugging Face Spaces enforces this; running as root
# also bites you on most other Docker hosts. UID 1000 is the convention.
RUN useradd --create-home --uid 1000 --shell /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Tasks live in SQLite. /app/data is writable by appuser; on hosts with a real
# persistent disk (e.g. Fly Volumes) mount the volume at /app/data and the same
# DATABASE_PATH keeps working unchanged.
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Run any pending migrations on container start so a fresh deploy boots into a
# usable state without a separate "release" command, then seed demo data once
# (the seed step is a no-op if tasks already exist) so a fresh volume isn't an
# empty UI for first-time visitors.
CMD ["sh", "-c", "python -m app.cli migrate && python -m app.cli seed-demo && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
