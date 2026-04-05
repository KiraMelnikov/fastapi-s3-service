def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FastAPI App" in response.text


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_no_auth_required(client):
    """Health and index endpoints must be public — no token needed."""
    response = client.get("/health")
    assert response.status_code == 200
