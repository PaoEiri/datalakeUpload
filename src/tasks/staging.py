from __future__ import annotations

import io
import pandas as pd
from prefect import task, get_run_logger
from sqlalchemy import text

from src.config import settings
from src.db.database import SessionLocal
from src.storage.minio_client import MinioClient


COLUMN_MAP = {
    "General, vivienda nueva y de segunda mano": "tipo_vivienda",
    "Total Nacional":                             "ambito",
    "Comunidades y Ciudades Autónomas":           "comunidad",
    "Índices y tasas":                            "indicador",
    "Periodo":                                    "periodo",
    "Total":                                      "valor",
}

TRIMESTRE_MES = {1: 1, 2: 4, 3: 7, 4: 10}


def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )


def _periodo_to_date(periodo: str) -> pd.Timestamp | None:
    """2025T4 → 2025-10-01"""
    try:
        anio = int(periodo[:4])
        trimestre = int(periodo[5:])
        mes = TRIMESTRE_MES.get(trimestre, 1)
        return pd.Timestamp(year=anio, month=mes, day=1)
    except Exception:
        return None


def _clean_ipv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_MAP)

    # Limpiar espacios
    for col in ["tipo_vivienda", "ambito", "comunidad", "indicador", "periodo"]:
        df[col] = df[col].astype(str).str.strip()

    # Comunidad vacía → "Nacional"
    df["comunidad"] = df["comunidad"].replace({"": "Nacional", "nan": "Nacional"})

    # Año y trimestre
    df["anio"] = df["periodo"].str[:4].astype(int)
    df["trimestre"] = df["periodo"].str[5:].astype(int)

    # Fecha: primer día del trimestre
    df["fecha"] = df["periodo"].apply(_periodo_to_date)

    # Valor: coma → punto, vacío → None
    df["valor"] = (
        df["valor"]
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
        .replace({"": None, "nan": None})
    )
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df["fuente"] = "INE - Índice de Precios de Vivienda"

    return df[[
        "tipo_vivienda", "ambito", "comunidad",
        "indicador", "anio", "trimestre", "fecha",
        "valor", "fuente",
    ]]


@task(name="ipv-minio-to-staging", retries=1)
def ipv_minio_to_staging(object_key: str) -> int:
    logger = get_run_logger()

    # 1. Leer de MinIO
    logger.info(f"Leyendo {object_key} de MinIO...")
    client = get_minio_client()
    body = client.get_object(object_key, bucket_name=settings.datasets_bucket)["Body"]

    df_raw = pd.read_csv(
        io.BytesIO(body.read()),
    sep=";",
    encoding="latin-1",   # ← antes era "utf-8"
    dtype=str,
    keep_default_na=False,
    )
    logger.info(f"Filas leídas: {len(df_raw)}")

    # 2. Limpiar
    df_clean = _clean_ipv(df_raw)
    logger.info(f"Filas tras limpieza: {len(df_clean)}")

    # 3. Insertar en staging (append — la tabla ya existe)
    with SessionLocal() as db:
        conn = db.connection()

        # Evitar duplicados si se recarga el mismo archivo:
        # borra solo las filas de esta fuente antes de reinsertar
        conn.execute(text(
            "DELETE FROM staging.ipv_precios_vivienda WHERE fuente = :fuente"
        ), {"fuente": "INE - Índice de Precios de Vivienda"})

        df_clean.to_sql(
            name="ipv_precios_vivienda",
            con=conn,
            schema="staging",
            if_exists="append",
            index=False,
        )
        db.commit()

    logger.info(f"Filas escritas en staging: {len(df_clean)}")
    return len(df_clean)