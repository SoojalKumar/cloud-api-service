"""Tests for database initialization and migrations."""

from app.database import connect, initialize_database
from app.migrations import get_applied_migrations


def test_initialize_database_applies_versioned_migrations(tmp_path) -> None:
    connection = connect(str(tmp_path / "app.db"))

    applied = initialize_database(connection)

    assert applied == ["001_create_tasks_table"]
    assert get_applied_migrations(connection) == {"001_create_tasks_table"}
    connection.close()


def test_initialize_database_is_idempotent(tmp_path) -> None:
    connection = connect(str(tmp_path / "app.db"))
    initialize_database(connection)

    applied = initialize_database(connection)

    assert applied == []
    connection.close()
