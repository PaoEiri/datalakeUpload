"""
Register a run's model in the MLflow Model Registry and manage aliases.

Usage:
    # Register and mark as challenger
    uv run src/register.py --run-id <RUN_ID> --config configs/config.yaml

    # Promote a version to champion
    uv run src/register.py --promote-version 3 --config configs/config.yaml
"""

import argparse
import os

import requests
import mlflow
import yaml
from mlflow import MlflowClient


def get_model_uri(run_id: str, tracking_uri: str, retries: int = 5, delay: float = 2.0) -> str:
    """Resolve model URI with retries — MLflow may async-commit logged model after run end."""
    import time

    client = MlflowClient(tracking_uri)
    experiment_id = client.get_run(run_id).info.experiment_id
    for attempt in range(retries):
        resp = requests.post(
            f"{tracking_uri}/api/2.0/mlflow/logged-models/search",
            json={"experiment_ids": [experiment_id], "filter_string": f"run_id = '{run_id}'", "max_results": 1},
        )
        resp.raise_for_status()
        models = resp.json().get("models", [])
        if models:
            return f"models:/{models[0]['info']['model_id']}"
        if attempt < retries - 1:
            time.sleep(delay)
    raise ValueError(f"No logged model found for run {run_id} after {retries} attempts")


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def register_as_challenger(run_id: str, config: dict) -> int:
    """Register model from run and assign the @challenger alias."""
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)

    model_name = config["registry"]["model_name"]
    challenger_alias = config["registry"]["challenger_alias"]

    model_uri = get_model_uri(run_id, tracking_uri)
    result = mlflow.register_model(model_uri=model_uri, name=model_name)
    version = result.version

    client = MlflowClient(tracking_uri)
    client.set_registered_model_alias(
        name=model_name,
        alias=challenger_alias,
        version=version,
    )

    print(f"\nRegistered '{model_name}' version {version} as @{challenger_alias}")
    print(f"Model URI: models:/{model_name}@{challenger_alias}")
    return version


def promote_to_champion(version: int, config: dict):
    """Move the @champion alias to the given version."""
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)

    model_name = config["registry"]["model_name"]
    champion_alias = config["registry"]["champion_alias"]
    challenger_alias = config["registry"]["challenger_alias"]

    client = MlflowClient(tracking_uri)

    # Remove challenger alias from this version (optional, keeps things clean)
    try:
        client.delete_registered_model_alias(name=model_name, alias=challenger_alias)
    except Exception:
        pass

    client.set_registered_model_alias(
        name=model_name,
        alias=champion_alias,
        version=version,
    )

    print(f"\nPromoted '{model_name}' version {version} to @{champion_alias}")
    print(f"Model URI: models:/{model_name}@{champion_alias}")


def compare_champion_vs_challenger(config: dict):
    """Print metrics for champion and challenger side by side."""
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri)
    model_name = config["registry"]["model_name"]

    def get_run_metrics(alias: str) -> dict:
        try:
            mv = client.get_model_version_by_alias(model_name, alias)
            run = client.get_run(mv.run_id)
            return {
                "version": mv.version,
                "run_id": mv.run_id,
                "metrics": run.data.metrics,
                "tags": run.data.tags,
            }
        except Exception:
            return None

    champion = get_run_metrics(config["registry"]["champion_alias"])
    challenger = get_run_metrics(config["registry"]["challenger_alias"])

    print("\n=== Champion vs Challenger ===")
    key_metrics = ["training_roc_auc", "training_f1_score", "training_accuracy_score"]

    header = f"{'Metric':<35} {'Champion':>12} {'Challenger':>12}"
    print(header)
    print("-" * len(header))

    for metric in key_metrics:
        champ_val = champion["metrics"].get(metric, "N/A") if champion else "N/A"
        chall_val = challenger["metrics"].get(metric, "N/A") if challenger else "N/A"
        cv = f"{champ_val:.4f}" if isinstance(champ_val, float) else champ_val
        clv = f"{chall_val:.4f}" if isinstance(chall_val, float) else chall_val
        print(f"{metric:<35} {cv:>12} {clv:>12}")

    if champion:
        print(f"\nChampion  → version {champion['version']} (run {champion['run_id'][:8]}...)")
    if challenger:
        print(f"Challenger → version {challenger['version']} (run {challenger['run_id'][:8]}...)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None, help="Run ID to register as challenger")
    parser.add_argument("--promote-version", type=int, default=None,
                        help="Model version to promote to champion")
    parser.add_argument("--compare", action="store_true",
                        help="Compare champion vs challenger metrics")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"]))

    if args.compare:
        compare_champion_vs_challenger(config)
    elif args.promote_version:
        promote_to_champion(args.promote_version, config)
    elif args.run_id:
        register_as_challenger(args.run_id, config)
    else:
        parser.print_help()
