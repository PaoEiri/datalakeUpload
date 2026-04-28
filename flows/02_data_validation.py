"""
Bloque 3 — Retries, fallos y observabilidad.

Demuestra retries automáticos en Prefect con un healthcheck a MLflow.

Ejecutar:
    uv run python flows/02_data_validation.py
    PREFECT_API_URL=http://localhost:4200/api uv run python flows/02_data_validation.py
"""

import os
import random

import pandas as pd
import requests
from prefect import flow, task
from prefect.logging import get_run_logger


@task(name="check-mlflow-health", retries=3, retry_delay_seconds=5)
def check_mlflow_health(tracking_uri: str) -> bool:
    """Verifica que MLflow responde — falla aleatoriamente para demo de retries."""
    logger = get_run_logger()
    # Probabilidad de fallo artificial en la demo (0.5 = 50% para la clase)
    if random.random() < 0.5:
        logger.warning("Simulated transient failure — will retry")
        raise ConnectionError("MLflow unreachable (simulated)")
    resp = requests.get(f"{tracking_uri}/health", timeout=5)
    resp.raise_for_status()
    logger.info(f"MLflow healthy at {tracking_uri}")
    return True


@task(name="load-and-validate")
def load_and_validate(path: str) -> dict:
    logger = get_run_logger()
    df = pd.read_csv(path)

    # Limpiar TotalCharges (columna problemática del dataset)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    nulls = df["TotalCharges"].isna().sum()
    if nulls > 0:
        logger.warning(f"Found {nulls} null TotalCharges — will be dropped")

    stats = {
        "rows": len(df),
        "columns": len(df.columns),
        "churn_rate": df["Churn"].map({"Yes": 1, "No": 0}).mean(),
        "null_totalcharges": int(nulls),
    }
    logger.info(f"Validation stats: {stats}")
    return stats


@flow(name="data-validation", log_prints=True)
def data_validation_flow(
    data_path: str = "data/raw/telco_churn.csv",
    tracking_uri: str | None = None,
):
    uri = tracking_uri or os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5001")
    check_mlflow_health(uri)
    stats = load_and_validate(data_path)
    print(f"Validation complete: {stats}")
    return stats


if __name__ == "__main__":
    data_validation_flow()
