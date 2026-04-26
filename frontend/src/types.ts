// Mirrors the backend Pydantic models in app/models/tasks.py.
// Hand-maintained for now; see frontend/README.md for the rationale.

export type TaskStatus = "todo" | "in_progress" | "done";

export const TASK_STATUSES: TaskStatus[] = ["todo", "in_progress", "done"];

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
}

export interface TaskSummary {
  total: number;
  todo: number;
  in_progress: number;
  done: number;
}

// Standard error envelope from app/errors.py.
export interface ApiErrorEnvelope {
  error: string;
  message: string;
  request_id: string;
}
