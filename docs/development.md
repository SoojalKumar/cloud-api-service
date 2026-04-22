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

- Replace the in-memory task store with a persistent database layer.
- Add authentication and role-aware access control.
- Add structured logging for production observability.
- Keep expanding test coverage as the API grows.

## API Quality Checklist

- New endpoints should include request and response models.
- List endpoints should support safe pagination defaults.
- Public responses should preserve request IDs and security headers.
- README examples should be updated when API behavior changes.
