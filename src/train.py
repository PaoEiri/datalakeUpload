"""
Training pipeline for churn prediction.

Usage:
    uv run src/train.py --config configs/config.yaml
    uv run src/train.py --config configs/config.yaml --model-type random_forest
"""

import argparse
import os

import mlflow
import mlflow.sklearn
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from data_prep import load_data

from xgboost import XGBClassifier


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_model(config: dict, model_type: str):
    params = config["model"][model_type]

    if model_type == "logistic_regression":
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(**params)),
        ])
        return model, params

    if model_type == "random_forest":
        return RandomForestClassifier(**params), params

    if model_type == "xgboost":
        return XGBClassifier(**params, eval_metric="logloss"), params

    raise ValueError(f"Unknown model type: {model_type}")


def train(config_path: str, model_type: str | None = None):
    config = load_config(config_path)
    model_type = model_type or config["model"]["type"]

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"]))
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    X_train, X_test, y_train, y_test = load_data(
        raw_path=config["data"]["raw_path"],
        test_size=config["data"]["test_size"],
        random_state=config["data"]["random_state"],
    )

    model, params = build_model(config, model_type)

    # autolog captures params, metrics, and the model automatically
    mlflow.sklearn.autolog(log_input_examples=True, log_model_signatures=True)

    with mlflow.start_run(run_name=model_type) as run:
        mlflow.set_tag("model_type", model_type)
        mlflow.set_tag("dataset", "telco-churn")

        model.fit(X_train, y_train)

        # Explicit log_model ensures the logged-model entity exists in MLflow 3.x
        # (autolog may not create it for Pipeline wrappers in all contexts)
        mlflow.sklearn.log_model(model, "model", input_example=X_train[:5])

        print(f"\nRun ID: {run.info.run_id}")
        print(f"Experiment: {config['mlflow']['experiment_name']}")
        print(f"Model: {model_type}")
        print(f"Params: {params}")
        print(f"\nView run at: {config['mlflow']['tracking_uri']}/#/experiments")

    return run.info.run_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--model-type", default=None,
                        choices=["logistic_regression", "random_forest", "xgboost"])
    args = parser.parse_args()

    train(args.config, args.model_type)
