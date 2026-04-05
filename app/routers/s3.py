# pylint: disable=function-redefined

from fastapi import APIRouter

from app.resources.sources import sources
from app.schemas.s3_schema import (
    S3DeleteResponse,
    S3ObjectCreatedResponse,
    S3ObjectResponse,
    S3ObjectsCreatedResponse,
    S3UploadBatchRequest,
    S3UploadEventRequest,
    S3UploadSingleEventRequest,
)
from app.services.s3 import s3_service

router = APIRouter(prefix="/s3", tags=["s3"])


@router.post(
    f"/single-event-receiver/it-dashboard/{sources.cyber_security_vulnerabilities}/upload",
    response_model=S3ObjectCreatedResponse,
)
async def upload_json(body: S3UploadSingleEventRequest) -> S3ObjectCreatedResponse:
    key = await s3_service.upload_single_event_json(
        source="single-event-receiver/it-dashboard/" + sources.cyber_security_vulnerabilities,
        data=body.content.model_dump(),
    )
    return S3ObjectCreatedResponse(key=key, message="Uploaded successfully.")


@router.post(  # type: ignore [no-redef]
    f"/event-receiver/it-dashboard/{sources.cyber_security_vulnerabilities}/upload",
    response_model=S3ObjectsCreatedResponse,
)
async def upload_json(body: S3UploadEventRequest) -> S3ObjectsCreatedResponse:
    keys = await s3_service.upload_event_json(
        source="event-receiver/it-dashboard/" + sources.cyber_security_vulnerabilities, data=body.content
    )
    return S3ObjectsCreatedResponse(keys=keys, message="Uploaded successfully.")


@router.post(  # type: ignore [no-redef]
    f"/batch-receiver/it-dashboard/{sources.cyber_security_vulnerabilities}/upload",
    response_model=S3ObjectCreatedResponse,
)
async def upload_json(body: S3UploadBatchRequest) -> S3ObjectCreatedResponse:
    key = await s3_service.upload_batch_json(
        source="batch-receiver/it-dashboard/" + sources.cyber_security_vulnerabilities,
        meta=body.meta,
        data=body.content,
    )
    return S3ObjectCreatedResponse(key=key, message="Uploaded successfully.")


@router.get("/system/{key:path}", response_model=S3ObjectResponse)
async def get_json(key: str) -> S3ObjectResponse:
    content = await s3_service.get_json(key)
    return S3ObjectResponse(content=content)


@router.delete("/system/{key:path}", response_model=S3DeleteResponse)
async def delete_object(key: str) -> S3DeleteResponse:
    await s3_service.delete_object(key)
    return S3DeleteResponse(key=key)
