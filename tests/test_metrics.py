def test_metrics_exposes_request_count_and_duration(client):
    client.get("/health")
    client.get("/api/tasks")
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
