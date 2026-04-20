"""Tests for task resource endpoints."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.tasks import task_service


client = TestClient(app)


def setup_function() -> None:
    task_service.clear()


def teardown_function() -> None:
    task_service.clear()


def test_create_and_list_tasks() -> None:
    create_response = client.post(
        "/api/v1/tasks",
        json={"title": "Ship API milestone", "description": "Add the first resource."},
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["id"]
    assert created_task["title"] == "Ship API milestone"
    assert created_task["description"] == "Add the first resource."
    assert created_task["status"] == "todo"

    list_response = client.get("/api/v1/tasks")

    assert list_response.status_code == 200
    assert list_response.json() == [created_task]


def test_get_update_and_delete_task() -> None:
    created_task = client.post(
        "/api/v1/tasks",
        json={"title": "Write tests"},
    ).json()

    get_response = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Write tests"

    update_response = client.patch(
        f"/api/v1/tasks/{created_task['id']}",
        json={"status": "in_progress", "description": "Cover CRUD behavior."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"
    assert update_response.json()["description"] == "Cover CRUD behavior."

    delete_response = client.delete(f"/api/v1/tasks/{created_task['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert missing_response.status_code == 404
    assert missing_response.json()["error"] == "not_found"


def test_task_validation_rejects_blank_title() -> None:
    response = client.post("/api/v1/tasks", json={"title": ""})

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
