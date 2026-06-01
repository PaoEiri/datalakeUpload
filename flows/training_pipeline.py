"""
Bloque 4 — Pipeline completo: Prefect orquesta MLflow.

Este es el fichero central de la Clase 2. Conecta los scripts existentes
de src/ con Prefect sin reescribirlos — solo los envuelve en @task.

Ejecutar manualmente:
    PREFECT_API_URL=${PREFECT_API_URL} uv run python flows/training_pipeline.py

Lanzar desde la UI: deployment "manual-training" (ver deploy.py)
"""

import sys

sys.path.insert(0, "src")

import yaml
from prefect import flow, task
from prefect.logging import get_run_logger

from evaluate import evaluate
from register import register_as_challenger
from train import train


@task(name="train-model", retries=1, retry_delay_seconds=10)
def task_train(config_path: str, model_type: str) -> str:
    logger = get_run_logger()
    run_id = train(config_path=config_path, model_type=model_type)
    logger.info(f"Training complete — run_id={run_id}")
    return run_id


@task(name="evaluate-model")
def task_evaluate(run_id: str, config_path: str) -> None:
    logger = get_run_logger()
    evaluate(run_id=run_id, config_path=config_path)
    logger.info(f"Evaluation complete for run_id={run_id}")


@task(name="register-challenger")
def task_register(run_id: str, config: dict) -> int:
    logger = get_run_logger()
    version = register_as_challenger(run_id=run_id, config=config)
    logger.info(f"Registered as challenger — version={version}")
    return version


@flow(name="churn-training-pipeline", log_prints=True)
def training_pipeline_flow(
    config_path: str = "configs/config.yaml",
    model_type: str = "xgboost",
) -> str:
    """Entrena, evalúa y registra un challenger en MLflow."""
    print(f"Starting training pipeline — model_type={model_type}")

    run_id = task_train(config_path, model_type)
    task_evaluate(run_id, config_path)

    with open(config_path) as f:
        config = yaml.safe_load(f)
    task_register(run_id, config)

    print(f"Pipeline complete — run_id={run_id}")
    return run_id


if __name__ == "__main__":
    training_pipeline_flow()
