from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IssuesSchema(BaseModel):
    id: int
    title: str


class VulnerabilityEventRequest(BaseModel):
    """Response model for S3 object creation"""

    count: int
    type: str
    issues: list[IssuesSchema]


class S3UploadMetadata(BaseModel):
    """Metadata for S3 upload"""

    model_config = ConfigDict(populate_by_name=True)

    write_mode_per_day: str = Field(default="overwrite", examples=["append/overwrite"], alias="writeModePerDay")


class S3UploadBatchRequest(BaseModel):
    """Request model for S3 upload"""

    meta: S3UploadMetadata
    content: dict[str, Any] = Field(..., examples=[{"key": "value"}])


class S3UploadEventRequest(BaseModel):
    """Request model for S3 upload"""

    content: VulnerabilityEventRequest


class S3UploadSingleEventRequest(BaseModel):
    """Request model for S3 upload"""

    content: IssuesSchema


class S3ObjectsCreatedResponse(BaseModel):
    """Response model for S3 object creation"""

    keys: list[str]
    message: str


class S3ObjectCreatedResponse(BaseModel):
    """Response model for S3 object creation"""

    key: str
    message: str


class S3ObjectResponse(BaseModel):
    """Response model for S3 object retrieval"""

    content: dict[str, Any] | None = Field(..., examples=[{"key": "value"}])


class S3DeleteResponse(BaseModel):
    """Response model for S3 object deletion"""

    key: str
    deleted: bool = True
