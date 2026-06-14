from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator


class Settings(BaseSettings):
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "postgres"
    database_url: str | None = None

    # MinIO
    minio_host: str = "minio"
    minio_port: int = 9000
    minio_console_port: int = 9001
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_secure: bool = False
    minio_endpoint: str | None = None

    # Buckets
    datasets_bucket: str = "datasets-upload"

    # Prefect
    prefect_api_host: str = "prefect-server"
    prefect_api_port: int = 4200
    prefect_api_url: str | None = None

    # API
    dataset_api_port: int = 8000

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def assemble_urls(self) -> "Settings":
        # Database URL
        if not self.database_url:
            self.database_url = (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

        # MinIO endpoint
        if not self.minio_endpoint:
            protocol = "https" if self.minio_secure else "http"
            self.minio_endpoint = f"{protocol}://{self.minio_host}:{self.minio_port}"

        # Prefect API URL
        if not self.prefect_api_url:
            self.prefect_api_url = (
                f"http://{self.prefect_api_host}:{self.prefect_api_port}/api"
            )

        return self


settings = Settings()
