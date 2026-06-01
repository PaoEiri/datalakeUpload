import asyncio
import io
import json

import pandas as pd
from prefect import flow, task
from prefect.logging import get_run_logger

from src.config import settings
from src.db import crud
from src.db.database import AsyncSessionLocal
from src.storage.minio_client import MinioClient


def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )


def _run_async(coro):
    return asyncio.run(coro)


async def _update_status(
    dataset_id: int,
    status: str,
    row_count: int | None = None,
    column_count: int | None = None,
    schema: list | None = None,
    preview: list | None = None,
    error_message: str | None = None,
) -> None:
    async with AsyncSessionLocal() as session:
        await crud.update_dataset_status(
            session=session,
            dataset_id=dataset_id,
            status=status,
            row_count=row_count,
            column_count=column_count,
            schema=schema,
            preview=preview,
            error_message=error_message,
        )


@task(name="set-dataset-validating")
def set_dataset_validating(dataset_id: int) -> None:
    _run_async(_update_status(dataset_id, status="validating"))


@task(name="set-dataset-ready")
def set_dataset_ready(
    dataset_id: int,
    row_count: int,
    column_count: int,
    schema: list,
    preview: list,
) -> None:
    _run_async(
        _update_status(
            dataset_id,
            status="ready",
            row_count=row_count,
            column_count=column_count,
            schema=schema,
            preview=preview,
        )
    )


@task(name="set-dataset-failed")
def set_dataset_failed(dataset_id: int, error_message: str) -> None:
    _run_async(_update_status(dataset_id, status="failed", error_message=error_message))


def _normalize_preview(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    preview = df.where(pd.notna(df), None).to_dict(orient="records")
    return preview


def _extract_csv_metadata(bucket_name: str, object_key: str) -> dict:
    client = get_minio_client()

    sample = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    df_preview = pd.read_csv(sample, nrows=20)
    if df_preview.shape[1] == 0:
        raise ValueError("El CSV no contiene columnas.")

    column_count = len(df_preview.columns)
    schema = [
        {"name": str(column), "dtype": str(dtype)}
        for column, dtype in zip(df_preview.columns, df_preview.dtypes)
    ]
    preview = _normalize_preview(df_preview)

    counter = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    row_count = sum(len(chunk) for chunk in pd.read_csv(counter, chunksize=100000))
    if row_count == 0:
        raise ValueError("El CSV está vacío.")

    return {
        "row_count": row_count,
        "column_count": column_count,
        "schema": schema,
        "preview": preview,
    }


def _extract_json_metadata(bucket_name: str, object_key: str) -> dict:
    client = get_minio_client()
    response = client.get_object(object_key, bucket_name=bucket_name)
    body = response["Body"].read()
    if not body.strip():
        raise ValueError("El JSON está vacío.")

    stripped = body.lstrip()
    if stripped.startswith(b"["):
        data = json.loads(body)
        if not isinstance(data, list):
            data = [data]
        if len(data) == 0:
            raise ValueError("El JSON no contiene registros.")
        df_preview = pd.DataFrame(data[:20])
        row_count = len(data)
    else:
        lines = [line for line in body.splitlines() if line.strip()]
        if len(lines) == 0:
            raise ValueError("El JSON no contiene registros.")
        row_count = len(lines)
        df_preview = pd.read_json(io.BytesIO(b"\n".join(lines)), lines=True, nrows=20)

    if df_preview.shape[1] == 0:
        raise ValueError("El JSON no contiene columnas válidas.")

    column_count = len(df_preview.columns)
    schema = [
        {"name": str(column), "dtype": str(dtype)}
        for column, dtype in zip(df_preview.columns, df_preview.dtypes)
    ]
    preview = _normalize_preview(df_preview)

    return {
        "row_count": row_count,
        "column_count": column_count,
        "schema": schema,
        "preview": preview,
    }


@task(name="extract-dataset-metadata")
def extract_metadata(bucket_name: str, object_key: str, file_format: str) -> dict:
    if file_format == "csv":
        return _extract_csv_metadata(bucket_name, object_key)
    return _extract_json_metadata(bucket_name, object_key)


@flow(name="dataset-management", log_prints=True)
def dataset_management_flow(
    dataset_id: int,
    bucket_name: str,
    object_key: str,
    file_format: str,
) -> None:
    logger = get_run_logger()
    logger.info("Dataset validation started: %s", object_key)
    set_dataset_validating(dataset_id)
    try:
        metadata = extract_metadata(bucket_name, object_key, file_format)
        set_dataset_ready(
            dataset_id,
            row_count=metadata["row_count"],
            column_count=metadata["column_count"],
            schema=metadata["schema"],
            preview=metadata["preview"],
        )
        logger.info("Dataset validated and metadata stored: %s", object_key)
    except Exception as exc:
        set_dataset_failed(dataset_id, error_message=str(exc))
        logger.error("Error procesando dataset %s: %s", object_key, exc)
        raise
