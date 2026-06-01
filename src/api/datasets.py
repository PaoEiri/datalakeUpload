import io
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from src.config import settings

from .schemas import (
    DatasetCreateResponse,
    DatasetListResponse,
    DatasetMetadata,
    DatasetPreviewResponse,
)
from src.db.database import AsyncSessionLocal
from src.db import crud
from src.storage.minio_client import MinioClient

router = APIRouter()


def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


def trigger_validation_flow(dataset_id: int, bucket_name: str, object_key: str, file_format: str) -> None:
    from flows.dataset_management import dataset_management_flow

    dataset_management_flow.submit(
        dataset_id=dataset_id,
        bucket_name=bucket_name,
        object_key=object_key,
        file_format=file_format,
    )


@router.post("/upload", response_model=DatasetCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db=Depends(get_db),
) -> DatasetCreateResponse:
    filename = file.filename or "uploaded_data"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".csv", ".json"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos CSV o JSON.",
        )

    file_format = "csv" if ext == ".csv" else "json"
    bucket_name = settings.datasets_bucket
    minio = get_minio_client()

    file.file.seek(0, os.SEEK_END)
    size_bytes = file.file.tell()
    file.file.seek(0)

    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no puede estar vacío.",
        )

    dataset_name = await crud.resolve_dataset_name(db, filename)
    storage_key = dataset_name

    try:
        minio.upload_fileobj(file.file, storage_key, bucket_name=bucket_name)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el fichero en storage: {exc}",
        )

    dataset = await crud.create_dataset_record(
        db,
        original_filename=filename,
        storage_key=storage_key,
        file_format=file_format,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        status="pending",
        dataset_name=dataset_name,
    )

    background_tasks.add_task(
        trigger_validation_flow,
        dataset.id,
        bucket_name,
        storage_key,
        file_format,
    )

    return DatasetCreateResponse(
        id=dataset.id,
        dataset_name=dataset.dataset_name,
        status=dataset.status,
        message="Carga aceptada. La validación y extracción de metadatos se ha programado.",
    )


@router.get("/", response_model=DatasetListResponse)
async def list_datasets(db=Depends(get_db)) -> DatasetListResponse:
    datasets = await crud.list_datasets(db)
    return DatasetListResponse(datasets=datasets)


@router.get("/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset(dataset_id: int, db=Depends(get_db)) -> DatasetMetadata:
    dataset = await crud.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset no encontrado.")
    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def get_dataset_preview(dataset_id: int, db=Depends(get_db)) -> DatasetPreviewResponse:
    dataset = await crud.get_dataset(db, dataset_id)
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
