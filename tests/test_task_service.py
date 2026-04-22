"""Tests for task service behavior."""

from app.models.tasks import TaskCreate, TaskStatus, TaskUpdate
from app.repositories.tasks import SQLiteTaskRepository
from app.services.tasks import TaskService


def test_task_service_persists_created_tasks(tmp_path) -> None:
    database_path = str(tmp_path / "service.db")
    service = TaskService(SQLiteTaskRepository(database_path))

    created_task = service.create_task(TaskCreate(title="Persistent task"))

    reloaded_service = TaskService(SQLiteTaskRepository(database_path))
    assert reloaded_service.get_task(created_task.id).title == "Persistent task"


def test_task_service_updates_and_summarizes_status(tmp_path) -> None:
    service = TaskService(SQLiteTaskRepository(str(tmp_path / "service.db")))
    first_task = service.create_task(TaskCreate(title="First"))
    second_task = service.create_task(TaskCreate(title="Second"))

    service.update_task(second_task.id, TaskUpdate(status=TaskStatus.DONE))
    summary = service.get_summary()

    assert service.get_task(first_task.id).status == TaskStatus.TODO
    assert summary.total == 2
    assert summary.todo == 1
    assert summary.done == 1
