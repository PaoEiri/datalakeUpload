from prefect import flow
from src.tasks.staging import ipv_minio_to_staging


@flow(name="staging-manual", log_prints=True)
def staging_manual(object_key: str):
    filas = ipv_minio_to_staging(object_key=object_key)
    print(f"Cargadas {filas} filas en staging")


if __name__ == "__main__":
    staging_manual(object_key="25171 (1).csv")