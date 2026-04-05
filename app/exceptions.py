from fastapi import HTTPException, status


class BucketNotFoundError(HTTPException):
    def __init__(self, bucket: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bucket '{bucket}' not found",
        )


class ObjectNotFoundError(HTTPException):
    def __init__(self, bucket: str, key: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object '{key}' not found in bucket '{bucket}'",
        )


class S3UploadError(HTTPException):
    def __init__(self, detail: str = "Failed to upload object"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class S3ConnectionError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 service is unavailable",
        )
