"""
Bloque 6 — Promoción automática de champion.

Compara AUC-ROC de @champion vs @challenger.
Si el challenger supera al champion por encima del threshold, lo promueve.

Ejecutar:
    PREFECT_API_URL=http://localhost:4200/api uv run python flows/champion_promotion.py
"""

import os
import sys

sys.path.insert(0, "src")

import mlflow
import yaml
from mlflow import MlflowClient
from prefect import flow, task
from prefect.logging import get_run_logger

from register import promote_to_champion


@task(name="compare-models")
def compare_models(config: dict, threshold: float = 0.005) -> tuple[bool, dict]:
    logger = get_run_logger()
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    model_name = config["registry"]["model_name"]

    def get_auc(alias: str) -> float | None:
        try:
            v = client.get_model_version_by_alias(model_name, alias)
            run = client.get_run(v.run_id)
            return run.data.metrics.get("roc_auc")
        except Exception as e:
            logger.warning(f"Could not get {alias} metrics: {e}")
            return None

    champion_auc = get_auc(config["registry"]["champion_alias"])
    challenger_auc = get_auc(config["registry"]["challenger_alias"])

    summary = {
        "champion_auc": champion_auc,
        "challenger_auc": challenger_auc,
        "threshold": threshold,
    }
    logger.info(f"Comparison: {summary}")

    if challenger_auc is None:
        logger.warning("No challenger found — skipping promotion")
        return False, summary

    if champion_auc is None:
        logger.info("No champion yet — promoting challenger unconditionally")
        return True, summary

    should_promote = (challenger_auc - champion_auc) > threshold
    summary["delta"] = challenger_auc - champion_auc
    return should_promote, summary


@task(name="promote-to-champion")
def task_promote(config: dict) -> None:
    logger = get_run_logger()
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    model_name = config["registry"]["model_name"]
    challenger_alias = config["registry"]["challenger_alias"]
    v = client.get_model_version_by_alias(model_name, challenger_alias)
    promote_to_champion(version=int(v.version), config=config)
    logger.info(f"Version {v.version} promoted to champion")


@flow(name="champion-promotion", log_prints=True)
def champion_promotion_flow(
    config_path: str = "configs/config.yaml",
    threshold: float = 0.005,
):
    """Promueve el challenger a champion si supera el threshold de mejora."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    should_promote, summary = compare_models(config, threshold)
    print(f"Comparison result: {summary}")

    if should_promote:
        task_promote(config)
        print("Challenger promoted to champion!")
    else:
        print("Champion retained — challenger did not meet threshold")


if __name__ == "__main__":
    champion_promotion_flow()
