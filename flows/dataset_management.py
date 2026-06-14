import io
import json
import os
import pandas as pd

from prefect import flow, task
from prefect.logging import get_run_logger

from src.config import settings
from src.db.database import SessionLocal
from src.db import crud_sync
from src.storage.minio_client import MinioClient


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


# ---------------------------------------------------------
# Tasks (SYNC)
# ---------------------------------------------------------
@task
def upload_to_minio(file_bytes: bytes, filename: str) -> tuple[str, str]:
    ext = os.path.splitext(filename)[1].lower()
    file_format = "csv" if ext == ".csv" else "json"
    storage_key = filename

    client = get_minio_client()
    client.upload_fileobj(io.BytesIO(file_bytes), storage_key, bucket_name=settings.datasets_bucket)

    return storage_key, file_format


@task
def create_dataset_record_task(filename, storage_key, file_format, content_type, size_bytes) -> int:
    with SessionLocal() as db:
        dataset_name = crud_sync.resolve_dataset_name(db, filename)
        dataset = crud_sync.create_dataset_record(
            db,
            original_filename=filename,
            storage_key=storage_key,
            file_format=file_format,
            content_type=content_type,
            size_bytes=size_bytes,
            status="pending",
            dataset_name=dataset_name,
        )
        return dataset.id


@task
def set_dataset_validating(dataset_id: int):
    with SessionLocal() as db:
        crud_sync.update_dataset_status(db, dataset_id, status="validating")


@task
def set_dataset_ready(dataset_id: int, row_count: int, column_count: int, schema: list, preview: list):
    with SessionLocal() as db:
        crud_sync.update_dataset_status(
            db,
            dataset_id,
            status="ready",
            row_count=row_count,
            column_count=column_count,
            schema=schema,
            preview=preview,
        )


@task
def set_dataset_failed(dataset_id: int, error_message: str):
    with SessionLocal() as db:
        crud_sync.update_dataset_status(
            db,
            dataset_id,
            status="failed",
            error_message=error_message,
        )


# ---------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------
def _normalize_preview(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    return df.where(pd.notna(df), None).to_dict(orient="records")


def _extract_csv_metadata(bucket_name: str, object_key: str) -> dict:
    client = get_minio_client()

    sample = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    df_preview = pd.read_csv(sample, nrows=20)

    if df_preview.shape[1] == 0:
        raise ValueError("El CSV no contiene columnas.")

    schema = [{"name": str(col), "dtype": str(dtype)} for col, dtype in zip(df_preview.columns, df_preview.dtypes)]
    preview = _normalize_preview(df_preview)

    counter = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    row_count = sum(len(chunk) for chunk in pd.read_csv(counter, chunksize=100000))

    if row_count == 0:
        raise ValueError("El CSV está vacío.")

    return {
        "row_count": row_count,
        "column_count": len(df_preview.columns),
        "schema": schema,
        "preview": preview,
    }


def _extract_json_metadata(bucket_name: str, object_key: str) -> dict:
    client = get_minio_client()
    body = client.get_object(object_key, bucket_name=bucket_name)["Body"].read()

    if not body.strip():
        raise ValueError("El JSON está vacío.")

    stripped = body.lstrip()

    if stripped.startswith(b"["):
        data = json.loads(body)
        df_preview = pd.DataFrame(data[:20])
        row_count = len(data)
    else:
        lines = [line for line in body.splitlines() if line.strip()]
        row_count = len(lines)
        df_preview = pd.read_json(io.BytesIO(b"\n".join(lines)), lines=True, nrows=20)

    if df_preview.shape[1] == 0:
        raise ValueError("El JSON no contiene columnas válidas.")

    schema = [{"name": str(col), "dtype": str(dtype)} for col, dtype in zip(df_preview.columns, df_preview.dtypes)]
    preview = _normalize_preview(df_preview)

    return {
        "row_count": row_count,
        "column_count": len(df_preview.columns),
        "schema": schema,
        "preview": preview,
    }


@task
def extract_metadata(bucket_name: str, object_key: str, file_format: str) -> dict:
    if file_format == "csv":
        return _extract_csv_metadata(bucket_name, object_key)
    return _extract_json_metadata(bucket_name, object_key)


# ---------------------------------------------------------
# FLOWS (SYNC)
# ---------------------------------------------------------
@flow(name="dataset-upload", log_prints=True)
def dataset_upload_flow(file_bytes: bytes, filename: str, content_type: str) -> int:
    logger = get_run_logger()
    logger.info(f"Starting upload for: {filename}")

    storage_key, file_format = upload_to_minio(file_bytes, filename)
    size_bytes = len(file_bytes)

    dataset_id = create_dataset_record_task(
        filename,
        storage_key,
        file_format,
        content_type,
        size_bytes,
    )

    dataset_management_flow(
        dataset_id=dataset_id,
        bucket_name=settings.datasets_bucket,
        object_key=storage_key,
        file_format=file_format,
    )

    return dataset_id


@flow(name="dataset-management")
def dataset_management_flow(dataset_id: int, bucket_name: str, object_key: str, file_format: str):
    logger = get_run_logger()
    logger.info(f"Validating dataset: {object_key}")

    set_dataset_validating(dataset_id)

    try:
        metadata = extract_metadata(bucket_name, object_key, file_format)

        set_dataset_ready(
            dataset_id,
            metadata["row_count"],
            metadata["column_count"],
            metadata["schema"],
            metadata["preview"],
        )

    except Exception as exc:
        set_dataset_failed(dataset_id, str(exc))
        raise
