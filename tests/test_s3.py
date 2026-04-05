from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.exceptions import BucketNotFoundError, ObjectNotFoundError
from app.services.s3 import S3Service


@pytest.fixture
def s3_service():
    with patch("app.services.s3.aioboto3.Session"):
        service = S3Service()
        service._verified_buckets = {"datalake"}
        yield service


def _make_async_client(mock_methods: dict | None = None):
    """Create a mock async context manager that returns a client with given methods."""
    client_mock = AsyncMock()
    if mock_methods:
        for name, value in mock_methods.items():
            setattr(client_mock, name, value)

    ctx = AsyncMock()
    ctx.__aenter__.return_value = client_mock
    ctx.__aexit__.return_value = None
    return ctx, client_mock


@pytest.mark.asyncio
async def test_upload_single_event(s3_service):
    ctx, client_mock = _make_async_client()
    s3_service._client = MagicMock(return_value=ctx)

    key = await s3_service.upload_single_event_json("test-source", {"id": 1, "title": "test"})

    assert "test-source/" in key
    assert "single-event-data-" in key
    client_mock.put_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_batch_overwrite(s3_service):
    ctx, client_mock = _make_async_client()
    s3_service._client = MagicMock(return_value=ctx)
    meta = MagicMock()
    meta.write_mode_per_day = "overwrite"

    key = await s3_service.upload_batch_json("test-source", meta, {"foo": "bar"})

    assert "batch-data.json" in key
    client_mock.put_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_batch_append(s3_service):
    ctx, client_mock = _make_async_client()
    s3_service._client = MagicMock(return_value=ctx)
    meta = MagicMock()
    meta.write_mode_per_day = "append"

    key = await s3_service.upload_batch_json("test-source", meta, {"foo": "bar"})

    assert "batch-data-" in key
    client_mock.put_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_json_success(s3_service):
    body_mock = AsyncMock()
    body_mock.read.return_value = b'{"foo": "bar"}'
    ctx, client_mock = _make_async_client()
    client_mock.get_object.return_value = {"Body": body_mock}
    s3_service._client = MagicMock(return_value=ctx)

    result = await s3_service.get_json("some/key.json")

    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_get_json_not_found(s3_service):
    ctx, client_mock = _make_async_client()
    client_mock.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
    )
    s3_service._client = MagicMock(return_value=ctx)

    with pytest.raises(ObjectNotFoundError):
        await s3_service.get_json("missing/key.json")


@pytest.mark.asyncio
async def test_delete_object_success(s3_service):
    ctx, client_mock = _make_async_client()
    s3_service._client = MagicMock(return_value=ctx)

    await s3_service.delete_object("some/key.json")

    client_mock.head_object.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_object_not_found(s3_service):
    ctx, client_mock = _make_async_client()
    client_mock.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not found"}}, "HeadObject"
    )
    s3_service._client = MagicMock(return_value=ctx)

    with pytest.raises(ObjectNotFoundError):
        await s3_service.delete_object("missing/key.json")


@pytest.mark.asyncio
async def test_ensure_bucket_not_found():
    with patch("app.services.s3.aioboto3.Session"):
        service = S3Service()
        ctx, client_mock = _make_async_client()
        client_mock.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not found"}}, "HeadBucket"
        )
        service._client = MagicMock(return_value=ctx)

        with pytest.raises(BucketNotFoundError):
            await service._ensure_bucket_exists("nonexistent")


@pytest.mark.asyncio
async def test_ensure_bucket_caches():
    with patch("app.services.s3.aioboto3.Session"):
        service = S3Service()
        ctx, client_mock = _make_async_client()
        service._client = MagicMock(return_value=ctx)

        await service._ensure_bucket_exists("datalake")
        await service._ensure_bucket_exists("datalake")

        client_mock.head_bucket.assert_awaited_once()


def test_batch_upload_schema_integration(client, auth_header):
    response = client.post(
        "/api/v1/s3/batch-receiver/it-dashboard/cyber-security-vulnerabilities/upload",
        json={"meta": {"writeModePerDay": "overwrite"}, "content": {"test": "data"}},
        headers=auth_header,
    )
    assert response.status_code in (200, 404, 502, 503)


def test_upload_missing_content_returns_422(client, auth_header):
    response = client.post(
        "/api/v1/s3/batch-receiver/it-dashboard/cyber-security-vulnerabilities/upload",
        json={},
        headers=auth_header,
    )
    assert response.status_code == 422
