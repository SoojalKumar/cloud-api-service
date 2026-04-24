# Development Workflow

This project is intentionally built in small, reviewable commits. Each change should be easy to explain, test, and roll back.

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
python -m pytest
```

## Commit Guidelines

- Keep commits focused on one behavior or structural improvement.
- Run tests before committing.
- Prefer adding tests with new endpoints or error behavior.
- Update README or docs when developer workflow changes.

## Current Development Priorities

The core service is feature-complete for a portfolio backend. Work from here should stay small and purposeful. Good next candidates:

- Add an additional resource alongside tasks to exercise the layering on a second domain.
- Evolve the shared API key into user accounts and role-aware authorization.
- Introduce structured JSON logging once a log aggregator is chosen.
- Add an actual hosted deployment example (Render, Fly.io, or Railway) under `docs/operations.md`.
- Keep expanding test coverage as new endpoints are added.

## API Quality Checklist

- New endpoints should include request and response models.
- List endpoints should support safe pagination defaults.
- Public responses should preserve request IDs and security headers.
- README examples should be updated when API behavior changes.
- Use the CLI and Makefile so local setup stays consistent across environments.

## Persistence Notes

The task API now uses a SQLite repository so local task data can survive application restarts. Keep generated database files out of git and use `DATABASE_PATH` when testing alternate storage locations.

## Authentication Notes

Mutating task endpoints now require `X-API-Key`. Keep the local development key in `.env` or exported shell variables, and update examples whenever protected routes change.
