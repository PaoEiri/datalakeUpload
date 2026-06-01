"""
Bloque 5 — Flujos programados y sub-flows.

Comprueba si el modelo champion supera max_age_days.
Si es así, lanza el training_pipeline como sub-flow (aparece anidado en la UI).

Schedule: diario a las 02:00 (configurado en deploy.py)
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, "src")

import mlflow
import yaml
from mlflow import MlflowClient
from prefect import flow, task
from prefect.logging import get_run_logger

from training_pipeline import training_pipeline_flow


@task(name="check-retraining-needed")
def check_retraining_needed(config: dict, max_age_days: int = 7) -> bool:
    logger = get_run_logger()
    tracking_uri = settings.mlflow_tracking_uri
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    model_name = config["registry"]["model_name"]
    champion_alias = config["registry"]["champion_alias"]

    try:
        version_info = client.get_model_version_by_alias(model_name, champion_alias)
        creation_ts = int(version_info.creation_timestamp) / 1000
        age_days = (datetime.now(timezone.utc).timestamp() - creation_ts) / 86400
        logger.info(f"Champion age: {age_days:.1f} days (threshold: {max_age_days})")
        needs_retrain = age_days > max_age_days
        if needs_retrain:
            logger.warning(f"Champion is {age_days:.1f} days old — retraining needed")
        return needs_retrain
    except Exception as e:
        logger.warning(f"No champion found ({e}) — triggering initial training")
        return True


@flow(name="retraining-trigger", log_prints=True)
def retraining_trigger_flow(
    config_path: str = "configs/config.yaml",
    max_age_days: int = 7,
    model_type: str = "xgboost",
):
    """Lanza re-entrenamiento si el champion es demasiado antiguo."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    needs_retrain = check_retraining_needed(config, max_age_days)

    if needs_retrain:
        print("Launching training sub-flow...")
        run_id = training_pipeline_flow(config_path=config_path, model_type=model_type)
        print(f"Retraining complete — run_id={run_id}")
    else:
        print("Champion is fresh — no retraining needed")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--model-type", default="xgboost")
    args = parser.parse_args()
    retraining_trigger_flow(
        config_path=args.config,
        max_age_days=args.max_age_days,
        model_type=args.model_type,
    )
