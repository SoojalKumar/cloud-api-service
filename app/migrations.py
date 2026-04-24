"""Lightweight SQLite migration support."""

from dataclasses import dataclass
import sqlite3


@dataclass(frozen=True)
class Migration:
    """A single database migration step."""

    version: str
    description: str
    statements: tuple[str, ...]


MIGRATIONS = (
    Migration(
        version="001_create_tasks_table",
        description="Create the tasks table.",
        statements=(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ),
    ),
)


def ensure_migration_table(connection: sqlite3.Connection) -> None:
    """Create the table used to track applied migrations."""

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()


def get_applied_migrations(connection: sqlite3.Connection) -> set[str]:
    """Return all migration versions already recorded in the database."""

    ensure_migration_table(connection)
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def apply_migrations(connection: sqlite3.Connection) -> list[str]:
    """Apply pending migrations in order and return newly applied versions."""

    ensure_migration_table(connection)
    applied = get_applied_migrations(connection)
    newly_applied: list[str] = []

    for migration in MIGRATIONS:
        if migration.version in applied:
            continue
        for statement in migration.statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (migration.version,),
        )
        connection.commit()
        newly_applied.append(migration.version)

    return newly_applied
