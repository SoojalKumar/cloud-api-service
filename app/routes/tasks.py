"""Task resource routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.models.tasks import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskSummaryResponse,
    TaskUpdate,
)
from app.security import require_api_key
from app.services.tasks import task_service


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a task that can be tracked by API clients."""

    return task_service.create_task(payload)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status: Optional[TaskStatus] = Query(default=None, description="Filter tasks by status."),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip."),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum tasks to return."),
) -> list[TaskResponse]:
    """Return tracked tasks with optional status filtering and pagination."""

    return task_service.list_tasks(status=status, offset=offset, limit=limit)


@router.get("/summary", response_model=TaskSummaryResponse)
def get_task_summary() -> TaskSummaryResponse:
    """Return aggregate task counts for lightweight dashboards."""

    return task_service.get_summary()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by ID."""

    return task_service.get_task(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(require_api_key)],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update task fields without replacing the full resource."""

    return task_service.update_task(task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_task(task_id: str) -> Response:
    """Delete a task after confirming it exists."""

    task_service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
