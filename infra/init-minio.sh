#!/bin/sh
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb --ignore-existing "local/$MLFLOW_ARTIFACT_BUCKET"
echo "Bucket '$MLFLOW_ARTIFACT_BUCKET' ready."
