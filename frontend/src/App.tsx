import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, api, apiBaseUrl, getStoredApiKey, storeApiKey } from "./api";
import type { Task, TaskStatus, TaskSummary } from "./types";
import { TASK_STATUSES } from "./types";

type StatusFilter = TaskStatus | "all";

interface Banner {
  kind: "info" | "error" | "success";
  message: string;
  requestId?: string | null;
}

function formatStatus(status: TaskStatus): string {
  return status.replace("_", " ");
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [summary, setSummary] = useState<TaskSummary | null>(null);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [loading, setLoading] = useState<boolean>(true);
  const [banner, setBanner] = useState<Banner | null>(null);
  const [apiKey, setApiKey] = useState<string>(getStoredApiKey());
  const [newTitle, setNewTitle] = useState<string>("");
  const [newDescription, setNewDescription] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);

  const showError = useCallback((err: unknown) => {
    if (err instanceof ApiError) {
      setBanner({ kind: "error", message: err.message, requestId: err.requestId });
    } else if (err instanceof Error) {
      setBanner({ kind: "error", message: err.message });
    } else {
      setBanner({ kind: "error", message: "Unknown error" });
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [list, sum] = await Promise.all([
        api.listTasks(filter === "all" ? undefined : { status: filter }),
        api.getSummary(),
      ]);
      setTasks(list);
      setSummary(sum);
      setBanner(null);
    } catch (err) {
      showError(err);
    } finally {
      setLoading(false);
    }
  }, [filter, showError]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const onSaveApiKey = (next: string) => {
    setApiKey(next);
    storeApiKey(next);
  };

  const onCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!newTitle.trim()) {
      return;
    }
    setSubmitting(true);
    try {
      await api.createTask({
        title: newTitle.trim(),
        description: newDescription.trim() || undefined,
      });
      setNewTitle("");
      setNewDescription("");
      setBanner({ kind: "success", message: "Task created." });
      await refresh();
    } catch (err) {
      showError(err);
    } finally {
      setSubmitting(false);
    }
  };

  const onCycleStatus = async (task: Task) => {
    const order: TaskStatus[] = ["todo", "in_progress", "done"];
    const next = order[(order.indexOf(task.status) + 1) % order.length];
    try {
      await api.updateTask(task.id, { status: next });
      await refresh();
    } catch (err) {
      showError(err);
    }
  };

  const onDelete = async (task: Task) => {
    if (!window.confirm(`Delete "${task.title}"?`)) {
      return;
    }
    try {
      await api.deleteTask(task.id);
      setBanner({ kind: "success", message: "Task deleted." });
      await refresh();
    } catch (err) {
      showError(err);
    }
  };

  const summaryCards = useMemo(() => {
    if (!summary) return null;
    const items: Array<{ label: string; value: number; tone: string }> = [
      { label: "Total", value: summary.total, tone: "total" },
      { label: "To do", value: summary.todo, tone: "todo" },
      { label: "In progress", value: summary.in_progress, tone: "in_progress" },
      { label: "Done", value: summary.done, tone: "done" },
    ];
    return (
      <section className="summary-grid" aria-label="Task summary">
        {items.map((item) => (
          <div key={item.label} className={`summary-card tone-${item.tone}`}>
            <div className="summary-card__value">{item.value}</div>
            <div className="summary-card__label">{item.label}</div>
          </div>
        ))}
      </section>
    );
  }, [summary]);

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Cloud-Based API Service</h1>
          <p className="muted">
            Demo UI for the FastAPI backend. Reads are public; writes require an API key.
          </p>
        </div>
        <div className="api-key">
          <label htmlFor="api-key-input">API key</label>
          <input
            id="api-key-input"
            type="password"
            placeholder="development-api-key"
            value={apiKey}
            onChange={(event) => onSaveApiKey(event.target.value)}
            autoComplete="off"
          />
        </div>
      </header>

      {banner && (
        <div className={`banner banner--${banner.kind}`} role="status">
          <span>{banner.message}</span>
          {banner.requestId && (
            <span className="banner__meta">request_id: {banner.requestId}</span>
          )}
        </div>
      )}

      {summaryCards}

      <section className="card">
        <h2>Create a task</h2>
        <form className="task-form" onSubmit={onCreate}>
          <input
            type="text"
            placeholder="Title"
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
            required
            maxLength={120}
          />
          <textarea
            placeholder="Description (optional)"
            value={newDescription}
            onChange={(event) => setNewDescription(event.target.value)}
            maxLength={500}
            rows={2}
          />
          <button type="submit" disabled={submitting || !newTitle.trim()}>
            {submitting ? "Creating…" : "Create task"}
          </button>
        </form>
      </section>

      <section className="card">
        <div className="card__header">
          <h2>Tasks</h2>
          <div className="filter">
            <label htmlFor="status-filter">Filter</label>
            <select
              id="status-filter"
              value={filter}
              onChange={(event) => setFilter(event.target.value as StatusFilter)}
            >
              <option value="all">All</option>
              {TASK_STATUSES.map((value) => (
                <option key={value} value={value}>
                  {formatStatus(value)}
                </option>
              ))}
            </select>
            <button type="button" className="link" onClick={() => void refresh()}>
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <p className="muted">Loading…</p>
        ) : tasks.length === 0 ? (
          <p className="muted">No tasks yet. Create one above.</p>
        ) : (
          <ul className="task-list">
            {tasks.map((task) => (
              <li key={task.id} className={`task-item status-${task.status}`}>
                <div className="task-item__main">
                  <div className="task-item__title">{task.title}</div>
                  {task.description && (
                    <div className="task-item__description">{task.description}</div>
                  )}
                  <div className="task-item__meta">
                    <span className={`status-pill status-${task.status}`}>
                      {formatStatus(task.status)}
                    </span>
                    <span className="muted">id: {task.id.slice(0, 8)}</span>
                  </div>
                </div>
                <div className="task-item__actions">
                  <button type="button" onClick={() => void onCycleStatus(task)}>
                    Advance
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => void onDelete(task)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer className="page__footer muted">
        <a href={`${apiBaseUrl()}/docs`} target="_blank" rel="noreferrer">
          OpenAPI / Swagger
        </a>
        <span>·</span>
        <a href={`${apiBaseUrl()}/api/v1/health`} target="_blank" rel="noreferrer">
          /health
        </a>
      </footer>
    </div>
  );
}
