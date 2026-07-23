"""Entry point manual/debug: reprocesa una fuente ya catalogada sin pasar
por un nuevo upload — descarga de MinIO el dataset actualmente vigente de
la fuente (fuentes_registradas.id_dataset_actual) y lo vuelve a cargar a
staging.<tabla> + dbt run acotado. Útil para reintentar tras un fallo de
staging sin re-subir el archivo.

Para vincular una subida NUEVA a una fuente, usa la API
(POST /datasets_upload/upload con id_fuente) — ese es el camino productivo
real (ver flows/dataset_management.py). Este script es solo para debugging.

Uso: docker exec -it prefect-worker python flows/04_staging_manual.py <id_fuente>
"""
import sys

from prefect import flow, get_run_logger

from src.config import settings
from src.db.database import SessionLocal
from src.db import crud_sync
from src.tasks.dbt import run_dbt
from src.tasks.staging_fuentes import cargar_fuente_a_staging
from src.storage.minio_client import MinioClient


def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )


@flow(name="staging-manual", log_prints=True)
def staging_manual(id_fuente: int):
    logger = get_run_logger()

    with SessionLocal() as db:
        fuente = crud_sync.get_fuente(db, id_fuente)
        if fuente is None:
            raise ValueError(f"Fuente {id_fuente} no encontrada")
        dataset = crud_sync.get_vigente_dataset_por_fuente(db, id_fuente)
        if dataset is None:
            raise ValueError(
                f"Fuente {fuente.codigo_fuente} (id={id_fuente}) no tiene ningún dataset vigente todavía"
            )

    logger.info(f"Reprocesando {fuente.codigo_fuente} desde {dataset.storage_key}")

    client = get_minio_client()
    file_bytes = client.get_object(dataset.storage_key, bucket_name=settings.datasets_bucket)["Body"].read()

    filas = cargar_fuente_a_staging(fuente.codigo_fuente, file_bytes)
    print(f"Cargadas {filas} filas en staging para {fuente.codigo_fuente}")

    run_dbt(select=f"{fuente.stg_modelo_destino}+")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python flows/04_staging_manual.py <id_fuente>")
        sys.exit(1)
    staging_manual(id_fuente=int(sys.argv[1]))
