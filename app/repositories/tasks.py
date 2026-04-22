"""SQLite repository for task persistence."""

from typing import Optional
import sqlite3

from app.database import connect, initialize_schema
from app.models.tasks import TaskResponse, TaskStatus


class SQLiteTaskRepository:
    """Persist task records in SQLite."""

    def __init__(self, database_path: str) -> None:
        self._connection = connect(database_path)
        initialize_schema(self._connection)

    def create(self, task: TaskResponse) -> TaskResponse:
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

    def get(self, task_id: str) -> Optional[TaskResponse]:
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
        self._connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._connection.commit()

    def clear(self) -> None:
        self._connection.execute("DELETE FROM tasks")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _to_task(row: sqlite3.Row) -> TaskResponse:
        return TaskResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=TaskStatus(row["status"]),
        )
