import os
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from src.config import settings
from src.db.database import SessionLocal
from src.db import crud_sync
from src.storage.minio_client import MinioClient

from prefect.utilities.asyncutils import run_sync_in_worker_thread

from .schemas import (
    DatasetCreateResponse,
    DatasetListResponse,
    DatasetMetadata,
    DatasetPreviewResponse,
)

router = APIRouter()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )


def get_db():
    """Dependencia síncrona para SQLAlchemy sync."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def trigger_upload_flow(
    file_bytes: bytes, filename: str, content_type: str, id_fuente: Optional[int] = None
) -> None:
    """Ejecuta el flow de Prefect en un worker thread."""
    from flows.dataset_management import dataset_upload_flow
    import anyio

    anyio.run(
        lambda: run_sync_in_worker_thread(
            dataset_upload_flow,
            file_bytes,
            filename,
            content_type,
            id_fuente,
        )
    )


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@router.post("/upload", response_model=DatasetCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_dataset(
    file: UploadFile = File(...),
    id_fuente: Optional[int] = Form(None),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db),
) -> DatasetCreateResponse:

    filename = file.filename or "uploaded_data"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in {".csv", ".json"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos CSV o JSON.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no puede estar vacío.",
        )

    if id_fuente is not None and crud_sync.get_fuente(db, id_fuente) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente {id_fuente} no encontrada en fuentes_registradas.",
        )

    content_type = file.content_type or "application/octet-stream"

    # Ejecutar el flow en background
    background_tasks.add_task(trigger_upload_flow, file_bytes, filename, content_type, id_fuente)

    return DatasetCreateResponse(
        id=0,
        dataset_name=filename,
        status="pending",
        message="Carga aceptada. El archivo se está procesando de forma asincrónica.",
        id_fuente=id_fuente,
    )


@router.get("/", response_model=DatasetListResponse)
async def list_datasets(db=Depends(get_db)) -> DatasetListResponse:
    datasets = crud_sync.list_datasets(db)
    return DatasetListResponse(datasets=datasets)


@router.get("/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset(dataset_id: int, db=Depends(get_db)) -> DatasetMetadata:
    dataset = crud_sync.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset no encontrado.")
    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def get_dataset_preview(dataset_id: int, db=Depends(get_db)) -> DatasetPreviewResponse:
    dataset = crud_sync.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset no encontrado.")

    if dataset.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Los metadatos aún no están listos. Intenta de nuevo en unos segundos.",
        )

    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        dataset_name=dataset.dataset_name,
        preview_rows=dataset.preview or [],
        schema=dataset.schema,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
    )
