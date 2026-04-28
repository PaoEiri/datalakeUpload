"""
Evaluate a logged model using mlflow.models.evaluate().

Generates: accuracy, F1, AUC-ROC, confusion matrix, ROC curve,
           precision-recall curve, and SHAP feature importance.

Usage:
    uv run src/evaluate.py --run-id <RUN_ID> --config configs/config.yaml
"""

import argparse
import os

import requests
import mlflow
import mlflow.models
import yaml
from mlflow import MlflowClient

from data_prep import load_data


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def get_model_uri(run_id: str, tracking_uri: str, retries: int = 5, delay: float = 2.0) -> str:
    """Resolve model URI for a run using MLflow 3.x logged models REST API.

    Retries because MLflow may async-commit the logged model after run end.
    """
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


def evaluate(run_id: str, config_path: str):
    config = load_config(config_path)

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    _, X_test, _, y_test = load_data(
        raw_path=config["data"]["raw_path"],
        test_size=config["data"]["test_size"],
        random_state=config["data"]["random_state"],
    )

    eval_df = X_test.copy()
    eval_df["Churn"] = y_test.values

    model_uri = get_model_uri(run_id, tracking_uri)
    print(f"Model URI: {model_uri}")

    with mlflow.start_run(run_id=run_id):
        result = mlflow.models.evaluate(
            model=model_uri,
            data=eval_df,
            targets="Churn",
            model_type="classifier",
            evaluators="default",
            evaluator_config={
                "log_model_explainability": True,
                "explainability_nsamples": 200,
            },
        )

    print("\n=== Evaluation Metrics ===")
    for name, value in result.metrics.items():
        print(f"  {name}: {value:.4f}" if isinstance(value, float) else f"  {name}: {value}")

    print(f"\nArtifacts logged to run: {run_id}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True, help="MLflow run ID to evaluate")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    evaluate(args.run_id, args.config)
