"""In-memory task service used by the first API resource."""

from uuid import uuid4

from app.errors import ResourceNotFoundError
from app.models.tasks import TaskCreate, TaskResponse, TaskStatus, TaskUpdate


class TaskService:
    """Manage tasks with a simple in-memory store.

    This intentionally starts in memory so the API contract can evolve before a
    database layer is introduced in a later milestone.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskResponse] = {}

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        task = TaskResponse(
            id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            status=TaskStatus.TODO,
        )
        self._tasks[task.id] = task
        return task

    def list_tasks(self) -> list[TaskResponse]:
        return list(self._tasks.values())

    def get_task(self, task_id: str) -> TaskResponse:
        try:
            return self._tasks[task_id]
        except KeyError as error:
            raise ResourceNotFoundError(f"Task '{task_id}' was not found.") from error

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskResponse:
        existing = self.get_task(task_id)
        updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
        self._tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: str) -> None:
        self.get_task(task_id)
        del self._tasks[task_id]

    def clear(self) -> None:
        """Reset service state for tests."""

        self._tasks.clear()


task_service = TaskService()
