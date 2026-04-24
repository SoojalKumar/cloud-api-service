"""SQLite database connection helpers."""

from pathlib import Path
import sqlite3


TASKS_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(database_path: str) -> sqlite3.Connection:
    """Create a SQLite connection and ensure parent folders exist."""

    path = Path(database_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create database tables required by the application."""

    connection.execute(TASKS_SCHEMA)
    connection.commit()


def database_ready(database_path: str) -> bool:
    """Return whether SQLite can be opened and queried successfully."""

    connection = connect(database_path)
    try:
        connection.execute("SELECT 1").fetchone()
        return True
    finally:
        connection.close()
