import datetime
import io
import json
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import aioboto3
from botocore.exceptions import ClientError, EndpointConnectionError

from app.config import settings
from app.exceptions import (
    BucketNotFoundError,
    ObjectNotFoundError,
    S3ConnectionError,
    S3UploadError,
)
from app.logger import get_logger
from app.protocols import UploadMeta
from app.schemas.s3_schema import VulnerabilityEventRequest

logger = get_logger(__name__)

DEFAULT_BUCKET_NAME = settings.minio_bucket_name


class S3Service:
    def __init__(self) -> None:
        self._session = aioboto3.Session()
        self._endpoint_url = f"{'https' if settings.minio_use_ssl == 'true' else 'http'}://{settings.minio_endpoint}"
        self._access_key = settings.minio_access_key
        self._secret_key = settings.minio_secret_key
        self._verified_buckets: set[str] = set()

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[Any]:
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        ) as client:
            yield client

    async def upload_single_event_json(self, source: str, data: dict[str, Any]) -> str | None:
        key = f"{source}/date={datetime.datetime.now().date()}/single-event-data-{uuid.uuid4()}.json"

        await self._ensure_bucket_exists(DEFAULT_BUCKET_NAME)
        try:
            body = json.dumps(data).encode()
            async with self._client() as client:
                await client.put_object(
                    Bucket=DEFAULT_BUCKET_NAME,
                    Key=key,
                    Body=io.BytesIO(body),
                    ContentType="application/json",
                    ContentLength=len(body),
                )
        except EndpointConnectionError:
            logger.error("S3 connection failed during upload: %s", key)
            raise S3ConnectionError()
        except ClientError as e:
            logger.error("S3 upload failed for key=%s: %s", key, e)
            raise S3UploadError(detail=str(e))

        logger.info("Uploaded %s to bucket %s", key, DEFAULT_BUCKET_NAME)
        return key

    async def upload_event_json(self, source: str, data: VulnerabilityEventRequest) -> list[str]:
        await self._ensure_bucket_exists(DEFAULT_BUCKET_NAME)
        keys = []

        async with self._client() as client:
            for issue in data.issues:
                key = f"{source}/date={datetime.datetime.now().date()}/event-data-{uuid.uuid4()}.json"
                try:
                    body = json.dumps(issue.model_dump()).encode()
                    await client.put_object(
                        Bucket=DEFAULT_BUCKET_NAME,
                        Key=key,
                        Body=io.BytesIO(body),
                        ContentType="application/json",
                        ContentLength=len(body),
                    )
                except EndpointConnectionError:
                    logger.error("S3 connection failed during upload: %s", key)
                    raise S3ConnectionError()
                except ClientError as e:
                    logger.error("S3 upload failed for key=%s: %s", key, e)
                    raise S3UploadError(detail=str(e))

                logger.info("Uploaded %s to bucket %s", key, DEFAULT_BUCKET_NAME)
                keys.append(key)
        return keys

    async def upload_batch_json(self, source: str, meta: UploadMeta, data: dict[str, Any]) -> str | None:
        write_mode = meta.write_mode_per_day
        await self._ensure_bucket_exists(DEFAULT_BUCKET_NAME)

        match write_mode:
            case "overwrite":
                key = f"{source}/date={datetime.datetime.now().date()}/batch-data.json"
            case "append":
                key = f"{source}/date={datetime.datetime.now().date()}/batch-data-{uuid.uuid4()}.json"
            case _:
                key = f"{source}/date={datetime.datetime.now().date()}/batch-data.json"

        try:
            body = json.dumps(data).encode()
            async with self._client() as client:
                await client.put_object(
                    Bucket=DEFAULT_BUCKET_NAME,
                    Key=key,
                    Body=io.BytesIO(body),
                    ContentType="application/json",
                    ContentLength=len(body),
                )
        except EndpointConnectionError:
            logger.error("S3 connection failed during upload: %s", key)
            raise S3ConnectionError()
        except ClientError as e:
            logger.error("S3 upload failed for key=%s: %s", key, e)
            raise S3UploadError(detail=str(e))

        logger.info("Uploaded %s to bucket %s (mode=%s)", key, DEFAULT_BUCKET_NAME, write_mode)
        return key

    async def get_json(self, key: str) -> Any | None:
        await self._ensure_bucket_exists(DEFAULT_BUCKET_NAME)
        try:
            async with self._client() as client:
                response = await client.get_object(Bucket=DEFAULT_BUCKET_NAME, Key=key)
                body = await response["Body"].read()
                logger.info("Retrieved %s from bucket %s", key, DEFAULT_BUCKET_NAME)
                return json.loads(body)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning("Object not found: %s/%s", DEFAULT_BUCKET_NAME, key)
                raise ObjectNotFoundError(DEFAULT_BUCKET_NAME, key)
            logger.error("S3 error getting key=%s: %s", key, e)
            raise S3ConnectionError()
        except EndpointConnectionError:
            logger.error("S3 connection failed during get: %s", key)
            raise S3ConnectionError()

    async def delete_object(self, key: str) -> None:
        await self._ensure_bucket_exists(DEFAULT_BUCKET_NAME)
        try:
            async with self._client() as client:
                await client.head_object(Bucket=DEFAULT_BUCKET_NAME, Key=key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.warning("Delete target not found: %s/%s", DEFAULT_BUCKET_NAME, key)
                raise ObjectNotFoundError(DEFAULT_BUCKET_NAME, key)
            logger.error("S3 error checking key=%s: %s", key, e)
            raise S3ConnectionError()

        try:
            async with self._client() as client:
                await client.delete_object(Bucket=DEFAULT_BUCKET_NAME, Key=key)
                logger.info("Deleted %s from bucket %s", key, DEFAULT_BUCKET_NAME)
        except EndpointConnectionError:
            logger.error("S3 connection failed during delete: %s", key)
            raise S3ConnectionError()

    async def _ensure_bucket_exists(self, bucket: str) -> None:
        if bucket in self._verified_buckets:
            return
        try:
            async with self._client() as client:
                await client.head_bucket(Bucket=bucket)
                self._verified_buckets.add(bucket)
                logger.info("Verified bucket exists: %s", bucket)
        except ClientError:
            logger.error("Bucket not found: %s", bucket)
            raise BucketNotFoundError(bucket)
        except EndpointConnectionError:
            logger.error("S3 connection failed checking bucket: %s", bucket)
            raise S3ConnectionError()


s3_service = S3Service()
