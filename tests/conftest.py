import os

os.environ.setdefault("MINIO_ACCESS_KEY", "testuser")
os.environ.setdefault("MINIO_SECRET_KEY", "testpassword")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_USE_SSL", "false")
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-for-hs256")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin")

import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_header():
    token = create_access_token(subject="test-user")
    return {"Authorization": f"Bearer {token}"}
