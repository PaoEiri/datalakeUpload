"""
Inference using the @champion model from the MLflow Model Registry.

Always loads the current @champion — no version hardcoding needed.

Usage:
    uv run src/predict.py --input data/raw/telco_churn.csv --config configs/config.yaml
"""

import argparse
import os

import mlflow
import mlflow.sklearn
import pandas as pd
import yaml

from data_prep import encode_features, load_and_clean


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_champion(config: dict):
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"]))
    model_name = config["registry"]["model_name"]
    alias = config["registry"]["champion_alias"]
    model_uri = f"models:/{model_name}@{alias}"
    print(f"Loading model: {model_uri}")
    return mlflow.sklearn.load_model(model_uri)


def predict(input_path: str, config_path: str):
    config = load_config(config_path)

    model = load_champion(config)

    df = load_and_clean(input_path)
    df_encoded = encode_features(df)

    # Drop target if present (running inference on raw data)
    X = df_encoded.drop(columns=["Churn"], errors="ignore")

    probabilities = model.predict_proba(X)[:, 1]
    predictions = model.predict(X)

    results = pd.DataFrame({
        "churn_probability": probabilities,
        "churn_prediction": predictions,
    })

    print(results.head(10).to_string(index=False))
    print(f"\nTotal predictions: {len(results)}")
    print(f"Predicted churn rate: {predictions.mean():.2%}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV with customer data")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    predict(args.input, args.config)
