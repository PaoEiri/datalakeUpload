#!/bin/sh
set -eu
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
DATASETS_BUCKET="${DATASETS_BUCKET:-datasets-upload}"
mc mb --ignore-existing "local/$DATASETS_BUCKET"
echo "Bucket '$DATASETS_BUCKET' ready."