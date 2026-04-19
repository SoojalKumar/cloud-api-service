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
pytest
```

## Commit Guidelines

- Keep commits focused on one behavior or structural improvement.
- Run tests before committing.
- Prefer adding tests with new endpoints or error behavior.
- Update README or docs when developer workflow changes.

## Current Development Priorities

- Add the first real business resource and CRUD endpoints.
- Strengthen environment-based configuration.
- Keep expanding test coverage as the API grows.
