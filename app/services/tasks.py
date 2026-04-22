"""Task service used by the first API resource."""

from typing import Optional
from uuid import uuid4

from app.config import settings
from app.errors import ResourceNotFoundError
from app.models.tasks import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskSummaryResponse,
    TaskUpdate,
)
from app.repositories.tasks import SQLiteTaskRepository


class TaskService:
    """Coordinate task business rules with the persistence layer."""

    def __init__(self, repository: Optional[SQLiteTaskRepository] = None) -> None:
        self._repository = repository or SQLiteTaskRepository(settings.database_path)

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        task = TaskResponse(
            id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            status=TaskStatus.TODO,
        )
        return self._repository.create(task)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[TaskResponse]:
        return self._repository.list(status=status, offset=offset, limit=limit)

    def get_summary(self) -> TaskSummaryResponse:
        tasks = self._repository.list(offset=0, limit=1000)
        return TaskSummaryResponse(
            total=len(tasks),
            todo=sum(task.status == TaskStatus.TODO for task in tasks),
            in_progress=sum(task.status == TaskStatus.IN_PROGRESS for task in tasks),
            done=sum(task.status == TaskStatus.DONE for task in tasks),
        )

    def get_task(self, task_id: str) -> TaskResponse:
        task = self._repository.get(task_id)
        if task is None:
            raise ResourceNotFoundError(f"Task '{task_id}' was not found.")
        return task

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskResponse:
        existing = self.get_task(task_id)
        updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
        return self._repository.update(updated)

    def delete_task(self, task_id: str) -> None:
        self.get_task(task_id)
        self._repository.delete(task_id)

    def clear(self) -> None:
        """Reset service state for tests."""

        self._repository.clear()


task_service = TaskService()
