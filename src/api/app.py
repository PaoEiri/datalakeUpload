from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .datasets import router as dataset_router
from src.config import settings
from src.storage.minio_client import MinioClient

app = FastAPI(
    title="Dataset Catalog API",
    version="0.1.0",
)
app.mount("/ui", StaticFiles(directory="src/ui"), name="ui")
# CORS (opcional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(dataset_router, prefix="/datasets_upload", tags=["datasets_upload"])


@app.on_event("startup")
async def on_startup() -> None:
    # Inicializar bucket de MinIO
    minio = MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )
    minio.ensure_bucket(settings.datasets_bucket)
