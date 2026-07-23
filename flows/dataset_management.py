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
from src.tasks.dbt import run_dbt
from src.tasks.staging_fuentes import cargar_fuente_a_staging
from src.tasks.dbt import run_dbt

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


@task
def marcar_dataset_no_vigente(dataset_id: int):
    with SessionLocal() as db:
        crud_sync.set_dataset_vigente(db, dataset_id, False)


@task
def marcar_vigencia_fuente(id_fuente: int, dataset_id: int):
    with SessionLocal() as db:
        crud_sync.marcar_dataset_vigente(db, id_fuente, dataset_id)


@task
def cargar_staging_fuente(id_fuente: int, bucket_name: str, object_key: str) -> tuple[str, int]:
    """Descarga el archivo vigente de MinIO y lo carga a staging.<tabla>
    según el codigo_fuente de la fuente registrada."""
    with SessionLocal() as db:
        fuente = crud_sync.get_fuente(db, id_fuente)
    if fuente is None:
        raise ValueError(f"Fuente {id_fuente} no encontrada")

    client = get_minio_client()
    file_bytes = client.get_object(object_key, bucket_name=bucket_name)["Body"].read()
    filas = cargar_fuente_a_staging(fuente.codigo_fuente, file_bytes)
    return fuente.stg_modelo_destino, filas


# ---------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------
def _normalize_preview(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    import json
    import math
    records = df.where(pd.notna(df), None).to_dict(orient="records")
    # Reemplaza float NaN/Inf que pandas no convierte a None correctamente
    cleaned = json.loads(
        json.dumps(records, default=lambda x: None if (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else x)
    )
    return cleaned

def _extract_csv_metadata(bucket_name: str, object_key: str) -> dict:
    client = get_minio_client()

    # --- Leer bytes del CSV desde MinIO ---
    obj = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    sample_bytes = obj.read()

    # --- Intentar varios encodings ---
    encodings = ["utf-8-sig", "latin1", "cp1252"]
    df_preview = None

    for enc in encodings:
        try:
            df_preview = pd.read_csv(
                io.BytesIO(sample_bytes),
                nrows=20,
                encoding=enc,
                sep=";"
            )
            break
        except UnicodeDecodeError:
            continue

    if df_preview is None:
        raise UnicodeDecodeError("No se pudo decodificar el CSV con los encodings comunes.")

    if df_preview.shape[1] == 0:
        raise ValueError("El CSV no contiene columnas.")

    # --- Schema ---
    schema = [
        {"name": str(col), "dtype": str(dtype)}
        for col, dtype in zip(df_preview.columns, df_preview.dtypes)
    ]

    preview = _normalize_preview(df_preview)

    # --- Contar filas de forma eficiente ---
    counter_obj = client.get_object(object_key, bucket_name=bucket_name)["Body"]
    row_count = 0

    for chunk in pd.read_csv(
        io.BytesIO(counter_obj.read()),
        chunksize=100000,
        encoding=enc,   # usar el encoding detectado
        sep=";"
    ):
        row_count += len(chunk)

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
def dataset_upload_flow(
    file_bytes: bytes, filename: str, content_type: str, id_fuente: int | None = None
) -> int:
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
        id_fuente=id_fuente,
    )

    return dataset_id


@flow(name="dataset-management")
def dataset_management_flow(
    dataset_id: int,
    bucket_name: str,
    object_key: str,
    file_format: str,
    id_fuente: int | None = None,
):
    """Flow 1: valida el archivo y, si viene vinculado a una fuente
    catalogada (id_fuente), aplica la lógica de vigencia y encadena la
    carga a staging (Flow 2) + dbt run acotado (Flow 3). Ver
    fuentes_registradas_y_api.md y consideraciones_prefect_flows.md."""
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

        if id_fuente is not None:
            # Orden importante: solo se marca vigente el dataset DESPUÉS de
            # que staging + dbt run hayan terminado con éxito. Si se marcara
            # antes y alguno de esos pasos fallara, fuentes_registradas
            # quedaría apuntando a un dataset cuyo staging nunca se cargó.
            stg_modelo_destino, filas = cargar_staging_fuente(id_fuente, bucket_name, object_key)
            logger.info(f"Cargadas {filas} filas en staging para {stg_modelo_destino}")
            run_dbt(select=f"{stg_modelo_destino}+")
            marcar_vigencia_fuente(id_fuente, dataset_id)

    except Exception as exc:
        set_dataset_failed(dataset_id, str(exc))
        if id_fuente is not None:
            marcar_dataset_no_vigente(dataset_id)
        raise
