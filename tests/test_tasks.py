def test_create_task(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Write report", "description": "Finish the DevOps write-up"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] > 0
    assert payload["title"] == "Write report"
    assert payload["description"] == "Finish the DevOps write-up"
    assert payload["is_completed"] is False
    assert payload["created_at"]


def test_list_tasks(client):
    client.post("/api/tasks", json={"title": "Task A"})
    client.post("/api/tasks", json={"title": "Task B"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Task B", "Task A"]


def test_get_task(client):
    created = client.post("/api/tasks", json={"title": "Inspect"}).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Inspect"


def test_update_task(client):
    created = client.post(
        "/api/tasks", json={"title": "Draft", "description": "v1"}
    ).json()
    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Final", "description": "v2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Final"
    assert payload["description"] == "v2"
    assert payload["is_completed"] is False


def test_complete_and_reopen_task(client):
    created = client.post("/api/tasks", json={"title": "Review"}).json()
    completed = client.patch(
        f"/api/tasks/{created['id']}", json={"is_completed": True}
    )
    assert completed.status_code == 200
    assert completed.json()["is_completed"] is True
    reopened = client.patch(
        f"/api/tasks/{created['id']}", json={"is_completed": False}
    )
    assert reopened.status_code == 200
    assert reopened.json()["is_completed"] is False


def test_delete_task(client):
    created = client.post("/api/tasks", json={"title": "Remove me"}).json()
    response = client.delete(f"/api/tasks/{created['id']}")
    assert response.status_code == 204
    missing = client.get(f"/api/tasks/{created['id']}")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Task not found"


def test_create_task_rejects_blank_title(client):
    response = client.post("/api/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_rejects_missing_title(client):
    response = client.post("/api/tasks", json={"description": "No title"})
    assert response.status_code == 422


def test_get_missing_task(client):
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_update_missing_task(client):
    response = client.patch("/api/tasks/999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_missing_task(client):
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404


def test_invalid_task_id(client):
    response = client.get("/api/tasks/not-an-id")
    assert response.status_code == 422


def test_home_page_renders_counts(client):
    client.post("/api/tasks", json={"title": "Visible task"})
    response = client.get("/")
    assert response.status_code == 200
    assert "Visible task" in response.text
    assert "TaskFlow" in response.text
