from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .datasets import router as dataset_router
from .fuentes import router as fuentes_router
from .consulta import router as consulta_router
from .indicadores_referencia import router as indicadores_referencia_router
from .predicciones import router as predicciones_router
from src.config import settings
from src.storage.minio_client import MinioClient

app = FastAPI(
    title="Dataset Catalog API",
    version="0.1.0",
)
app.mount("/ui", StaticFiles(directory="src/ui", html=True), name="ui")
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
app.include_router(fuentes_router, prefix="/fuentes_registradas", tags=["fuentes_registradas"])
app.include_router(consulta_router, prefix="/consulta", tags=["consulta"])
app.include_router(
    indicadores_referencia_router, prefix="/indicadores_referencia", tags=["indicadores_referencia"]
)
app.include_router(predicciones_router, prefix="/predicciones", tags=["predicciones"])


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
