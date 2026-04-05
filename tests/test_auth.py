from datetime import timedelta

import jwt
import pytest

from app.auth import create_access_token
from app.config import settings


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/v1/s3/system/some/key")
    assert response.status_code in (401, 403)


def test_protected_endpoint_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/s3/system/some/key",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_protected_endpoint_rejects_expired_token(client):
    token = create_access_token(subject="test-user", expires_delta=timedelta(seconds=-1))
    response = client.get(
        "/api/v1/s3/system/some/key",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"]


def test_protected_endpoint_accepts_valid_token(client, auth_header):
    response = client.get("/api/v1/s3/system/some/key", headers=auth_header)
    # Will fail on S3 connection, but auth passed (not 401/403)
    assert response.status_code in (200, 404, 502, 503)


def test_create_access_token_contains_subject():
    token = create_access_token(subject="my-service")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "my-service"
    assert "exp" in payload
    assert "iat" in payload


def test_token_missing_subject_rejected(client):
    payload = {"exp": 9999999999}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    response = client.get(
        "/api/v1/s3/system/some/key",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "missing subject" in response.json()["detail"]


def test_login_success(client):
    response = client.post("/auth/token", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post("/auth/token", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_wrong_username(client):
    response = client.post("/auth/token", json={"username": "unknown", "password": "admin"})
    assert response.status_code == 401


def test_login_token_works_on_protected_route(client):
    login = client.post("/auth/token", json={"username": "admin", "password": "admin"})
    token = login.json()["access_token"]
    response = client.get(
        "/api/v1/s3/system/some/key",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 404, 502, 503)
