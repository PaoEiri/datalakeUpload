from fastapi import FastAPI

from .datasets import router as dataset_router
from src.config import settings
from src.storage.minio_client import MinioClient
from src.db.database import init_db


app = FastAPI(title="Dataset Catalog API", version="0.1.0")
app.include_router(dataset_router, prefix="/datasets_upload", tags=["datasets_upload"])


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()

    minio = MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )
    minio.ensure_bucket(settings.datasets_bucket)
