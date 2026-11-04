from app.main import engine


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"


def test_health_unhealthy_when_database_fails(client, monkeypatch):
    def fail_connect():
        raise RuntimeError("database is unavailable")

    monkeypatch.setattr(engine, "connect", fail_connect)
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert payload["database"] == "disconnected"
    assert "unavailable" in payload["detail"]
