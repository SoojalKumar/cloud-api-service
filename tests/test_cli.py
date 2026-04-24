"""Tests for the project management CLI."""

import json

from app.cli import main
from app.repositories.tasks import SQLiteTaskRepository


def test_cli_migrate_and_seed_demo(tmp_path, capsys) -> None:
    database_path = str(tmp_path / "cli.db")

    assert main(["migrate", "--database-path", database_path]) == 0
    assert main(["seed-demo", "--database-path", database_path]) == 0

    repository = SQLiteTaskRepository(database_path)
    try:
        tasks = repository.list(limit=10)
        assert len(tasks) == 3
    finally:
        repository.close()

    output = capsys.readouterr().out
    assert "Applied migrations" in output
    assert "Seeded 3 demo tasks." in output


def test_cli_reset_requires_confirmation(tmp_path, capsys) -> None:
    database_path = str(tmp_path / "cli.db")

    result = main(["reset-db", "--database-path", database_path])

    assert result == 1
    assert "without --yes" in capsys.readouterr().out


def test_cli_show_config_outputs_json(capsys) -> None:
    assert main(["show-config"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["auth_mode"] == "api_key"
    assert "database_path" in payload
