# Operations Guide

## Local Commands

Use the included `Makefile` for the most common workflows:

```bash
make run
make test
make migrate
make seed-demo
make reset-db
make show-config
```

You can also call the CLI directly:

```bash
python -m app.cli migrate
python -m app.cli seed-demo
python -m app.cli reset-db --yes
python -m app.cli show-config
```

## Database Lifecycle

- `migrate` applies pending SQLite schema migrations.
- `seed-demo` populates a fresh database with demo tasks for local testing.
- `reset-db --yes` deletes the SQLite database file so you can rebuild from scratch.

## Recommended Local Flow

```bash
cp .env.example .env
make migrate
make seed-demo
make run
```

Then open `http://127.0.0.1:8000/docs` and exercise the API.

## Deployment Notes

- Set `APP_ENV=production` in hosted environments.
- Provide a strong `API_KEY` value instead of the local development default.
- Point `DATABASE_PATH` at a persistent volume or mounted storage location.
- Run migrations before or during deployment startup.
