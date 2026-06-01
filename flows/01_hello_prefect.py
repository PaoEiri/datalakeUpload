"""
Bloque 2 — Introducción a Prefect: @flow, @task, logging.
 1. export PREFECT_API_URL="${PREFECT_API_URL}" 2. ejecutar el deploy.py
Se puede ejecutar sin servidor Prefect activo:
    uv run python flows/01_hello_prefect.py

Con servidor activo (para ver en la UI):
    PREFECT_API_URL=${PREFECT_API_URL} uv run python flows/01_hello_prefect.py
"""

import pandas as pd
from prefect import flow, task
from prefect.logging import get_run_logger


@task(name="fetch-data")
def fetch_data(path: str) -> pd.DataFrame:
    logger = get_run_logger()
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


@task(name="validate-shape")
def validate_shape(df: pd.DataFrame, min_rows: int = 5000) -> bool:
    logger = get_run_logger()
    n = len(df)
    if n < min_rows:
        raise ValueError(f"Dataset too small: {n} rows (minimum {min_rows})")
    logger.info(f"Shape OK: {df.shape}")
    return True


@flow(name="hello-prefect", log_prints=True)
def hello_flow(data_path: str = "data/raw/telco_churn.csv"):
    print("Starting hello-prefect flow")
    df = fetch_data(data_path)
    validate_shape(df)
    print(f"Flow complete — {len(df)} rows validated")


if __name__ == "__main__":
    import os

    from src.config import settings

    os.environ.setdefault("PREFECT_API_URL", settings.prefect_api_url)
    hello_flow()
