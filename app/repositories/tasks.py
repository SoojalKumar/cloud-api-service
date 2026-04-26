"""SQLite repository for task persistence."""

from threading import Lock
from typing import Optional
import sqlite3

from app.database import connect, initialize_database
from app.models.tasks import TaskResponse, TaskStatus


class SQLiteTaskRepository:
    """Persist task records in SQLite.

    The connection is shared across threads (FastAPI runs sync endpoints in a
    threadpool) so all access is serialized through ``_lock``. SQLite is fast
    enough that this is not a meaningful bottleneck for the project's scale,
    and it avoids the segfaults that arise when multiple threads concurrently
    use the same ``sqlite3.Connection``.
    """

    def __init__(self, database_path: str) -> None:
        self._connection = connect(database_path)
        self._lock = Lock()
        initialize_database(self._connection)

    def create(self, task: TaskResponse) -> TaskResponse:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO tasks (id, title, description, status)
                VALUES (?, ?, ?, ?)
                """,
                (task.id, task.title, task.description, task.status.value),
            )
            self._connection.commit()
        return task

    def list(
        self,
        status: Optional[TaskStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[TaskResponse]:
        with self._lock:
            if status is None:
                rows = self._connection.execute(
                    """
                    SELECT id, title, description, status
                    FROM tasks
                    ORDER BY rowid
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                ).fetchall()
            else:
                rows = self._connection.execute(
                    """
                    SELECT id, title, description, status
                    FROM tasks
                    WHERE status = ?
                    ORDER BY rowid
                    LIMIT ? OFFSET ?
                    """,
                    (status.value, limit, offset),
                ).fetchall()
        return [self._to_task(row) for row in rows]

    def status_counts(self) -> dict[str, int]:
        """Return per-status totals using a single grouped aggregate.

        Computing the summary from a paginated ``list()`` capped at 1000 rows
        was silently wrong as soon as the table grew past the cap. SQL keeps
        this exact at any scale.
        """

        with self._lock:
            rows = self._connection.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM tasks
                GROUP BY status
                """,
            ).fetchall()
        counts: dict[str, int] = {status.value: 0 for status in TaskStatus}
        for row in rows:
            counts[row["status"]] = row["count"]
        return counts

    def get(self, task_id: str) -> Optional[TaskResponse]:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT id, title, description, status
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return self._to_task(row)

    def update(self, task: TaskResponse) -> TaskResponse:
        with self._lock:
            self._connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (task.title, task.description, task.status.value, task.id),
            )
            self._connection.commit()
        return task

    def delete(self, task_id: str) -> None:
        with self._lock:
            self._connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self._connection.commit()

    def clear(self) -> None:
        with self._lock:
            self._connection.execute("DELETE FROM tasks")
            self._connection.commit()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    @staticmethod
    def _to_task(row: sqlite3.Row) -> TaskResponse:
        return TaskResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=TaskStatus(row["status"]),
        )
