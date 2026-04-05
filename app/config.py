from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = Field(..., validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., validation_alias="MINIO_SECRET_KEY")
    minio_use_ssl: str = Field(default="true", validation_alias="MINIO_USE_SSL")
    minio_bucket_name: str = Field(default="datalake", validation_alias="MINIO_BUCKET_NAME")

    jwt_secret: str = Field(..., validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=30, validation_alias="JWT_EXPIRATION_MINUTES")

    admin_username: str = Field(..., validation_alias="ADMIN_USERNAME")
    admin_password: str = Field(..., validation_alias="ADMIN_PASSWORD")


settings = Settings()  # type: ignore [call-arg]
