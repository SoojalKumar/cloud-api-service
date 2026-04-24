"""Project management CLI for local operations."""

import argparse
import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.config import settings
from app.database import connect, initialize_database
from app.models.tasks import TaskResponse, TaskStatus
from app.repositories.tasks import SQLiteTaskRepository


DEMO_TASKS = (
    ("Review deployment checklist", "Prepare the service for a staging deploy.", TaskStatus.TODO),
    ("Instrument API latency", "Track request timing for key routes.", TaskStatus.IN_PROGRESS),
    ("Publish README updates", "Document the latest runtime and auth behavior.", TaskStatus.DONE),
)


def _database_path(value: Optional[str]) -> str:
    return value or settings.database_path



def migrate(database_path: str) -> int:
    connection = connect(database_path)
    try:
        applied = initialize_database(connection)
    finally:
        connection.close()

    if applied:
        print(f"Applied migrations: {', '.join(applied)}")
    else:
        print("No pending migrations.")
    return 0



def seed_demo(database_path: str) -> int:
    repository = SQLiteTaskRepository(database_path)
    try:
        existing_tasks = repository.list(limit=1)
        if existing_tasks:
            print("Database already contains tasks; skipping demo seed.")
            return 0

        for title, description, status in DEMO_TASKS:
            repository.create(
                TaskResponse(
                    id=str(uuid4()),
                    title=title,
                    description=description,
                    status=status,
                )
            )
    finally:
        repository.close()

    print(f"Seeded {len(DEMO_TASKS)} demo tasks.")
    return 0



def reset_db(database_path: str, confirmed: bool) -> int:
    if not confirmed:
        print("Refusing to delete the database without --yes.")
        return 1

    path = Path(database_path)
    if path.exists():
        path.unlink()
        print(f"Removed database: {database_path}")
    else:
        print("Database file did not exist; nothing to remove.")
    return 0



def show_config() -> int:
    print(
        json.dumps(
            {
                "app_name": settings.app_name,
                "environment": settings.environment,
                "database_path": settings.database_path,
                "log_level": settings.log_level,
                "auth_mode": "api_key",
            },
            indent=2,
        )
    )
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cloud API Service management commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate_parser = subparsers.add_parser("migrate", help="Apply pending database migrations")
    migrate_parser.add_argument("--database-path", default=None)

    seed_parser = subparsers.add_parser("seed-demo", help="Seed the database with demo tasks")
    seed_parser.add_argument("--database-path", default=None)

    reset_parser = subparsers.add_parser("reset-db", help="Delete the SQLite database file")
    reset_parser.add_argument("--database-path", default=None)
    reset_parser.add_argument("--yes", action="store_true", help="Confirm destructive reset")

    subparsers.add_parser("show-config", help="Print resolved runtime configuration")
    return parser



def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "migrate":
        return migrate(_database_path(args.database_path))
    if args.command == "seed-demo":
        return seed_demo(_database_path(args.database_path))
    if args.command == "reset-db":
        return reset_db(_database_path(args.database_path), args.yes)
    if args.command == "show-config":
        return show_config()

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
