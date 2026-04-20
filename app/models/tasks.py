"""Task resource request and response models."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    """Payload for creating a task."""

    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class TaskUpdate(BaseModel):
    """Payload for partially updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    """Task returned by the API."""

    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
