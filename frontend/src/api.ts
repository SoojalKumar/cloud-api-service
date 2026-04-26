import type {
  ApiErrorEnvelope,
  Task,
  TaskCreate,
  TaskStatus,
  TaskSummary,
  TaskUpdate,
} from "./types";

// In dev, vite.config.ts proxies /api → backend at localhost:8000.
// In prod, set VITE_API_BASE_URL to the deployed backend's origin.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

const API_KEY_STORAGE_KEY = "cloud-api-service:api-key";

export function getStoredApiKey(): string {
  return window.localStorage.getItem(API_KEY_STORAGE_KEY) ?? "";
}

export function storeApiKey(value: string): void {
  if (value) {
    window.localStorage.setItem(API_KEY_STORAGE_KEY, value);
  } else {
    window.localStorage.removeItem(API_KEY_STORAGE_KEY);
  }
}

// Surfacing both the human message and the request_id makes server logs
// usable from the UI when something goes wrong.
export class ApiError extends Error {
  readonly status: number;
  readonly requestId: string | null;
  readonly code: string;

  constructor(status: number, envelope: Partial<ApiErrorEnvelope>) {
    super(envelope.message ?? `Request failed with status ${status}`);
    this.status = status;
    this.code = envelope.error ?? "unknown_error";
    this.requestId = envelope.request_id ?? null;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  authenticated?: boolean;
  query?: Record<string, string | number | undefined>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, authenticated = false, query } = options;

  const url = new URL(`${API_BASE_URL}${path}`, window.location.origin);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (authenticated) {
    const key = getStoredApiKey();
    if (!key) {
      throw new ApiError(401, {
        error: "missing_api_key",
        message: "API key required for this action. Set it in the header.",
        request_id: "client",
      });
    }
    headers["X-API-Key"] = key;
  }

  const response = await fetch(url.toString().replace(window.location.origin, ""), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as unknown) : null;

  if (!response.ok) {
    throw new ApiError(response.status, (payload ?? {}) as Partial<ApiErrorEnvelope>);
  }

  return payload as T;
}

export const api = {
  listTasks(filter?: { status?: TaskStatus }): Promise<Task[]> {
    return request<Task[]>("/api/v1/tasks", { query: { status: filter?.status } });
  },
  getSummary(): Promise<TaskSummary> {
    return request<TaskSummary>("/api/v1/tasks/summary");
  },
  createTask(payload: TaskCreate): Promise<Task> {
    return request<Task>("/api/v1/tasks", {
      method: "POST",
      body: payload,
      authenticated: true,
    });
  },
  updateTask(id: string, payload: TaskUpdate): Promise<Task> {
    return request<Task>(`/api/v1/tasks/${id}`, {
      method: "PATCH",
      body: payload,
      authenticated: true,
    });
  },
  deleteTask(id: string): Promise<void> {
    return request<void>(`/api/v1/tasks/${id}`, {
      method: "DELETE",
      authenticated: true,
    });
  },
};
