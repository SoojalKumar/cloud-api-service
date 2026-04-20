"""Task resource routes."""

from fastapi import APIRouter, Response, status

from app.models.tasks import TaskCreate, TaskResponse, TaskUpdate
from app.services.tasks import task_service


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a task that can be tracked by API clients."""

    return task_service.create_task(payload)


@router.get("", response_model=list[TaskResponse])
def list_tasks() -> list[TaskResponse]:
    """Return all tracked tasks in insertion order."""

    return task_service.list_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by ID."""

    return task_service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update task fields without replacing the full resource."""

    return task_service.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> Response:
    """Delete a task after confirming it exists."""

    task_service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
