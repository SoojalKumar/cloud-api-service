"""SQLite database connection helpers."""

from pathlib import Path
import sqlite3

from app.migrations import apply_migrations


def connect(database_path: str) -> sqlite3.Connection:
    """Create a SQLite connection and ensure parent folders exist."""

    path = Path(database_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection) -> list[str]:
    """Apply pending migrations required by the application."""

    return apply_migrations(connection)


def database_ready(database_path: str) -> bool:
    """Return whether SQLite can be opened and queried successfully."""

    connection = connect(database_path)
    try:
        connection.execute("SELECT 1").fetchone()
        return True
    finally:
        connection.close()
