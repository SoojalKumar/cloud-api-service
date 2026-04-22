"""Tests for the SQLite task repository."""

from app.models.tasks import TaskResponse, TaskStatus
from app.repositories.tasks import SQLiteTaskRepository


def test_sqlite_task_repository_persists_tasks(tmp_path) -> None:
    database_path = str(tmp_path / "tasks.db")
    repository = SQLiteTaskRepository(database_path)
    task = TaskResponse(
        id="task-1",
        title="Persist me",
        description="Stored in SQLite",
        status=TaskStatus.TODO,
    )

    repository.create(task)
    repository.close()

    reopened_repository = SQLiteTaskRepository(database_path)

    assert reopened_repository.get("task-1") == task
    reopened_repository.close()


def test_sqlite_task_repository_filters_and_paginates(tmp_path) -> None:
    repository = SQLiteTaskRepository(str(tmp_path / "tasks.db"))
    repository.create(TaskResponse(id="1", title="One", description=None, status=TaskStatus.TODO))
    repository.create(TaskResponse(id="2", title="Two", description=None, status=TaskStatus.DONE))
    repository.create(TaskResponse(id="3", title="Three", description=None, status=TaskStatus.DONE))

    tasks = repository.list(status=TaskStatus.DONE, offset=1, limit=1)

    assert [task.id for task in tasks] == ["3"]
    repository.close()
