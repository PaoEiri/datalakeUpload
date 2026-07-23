"""Carga las 13 fuentes reales de dataset/ a staging.*, para el dataset de
referencia del TFM. Reutiliza los mismos parsers que el pipeline productivo
(src/tasks/staging_fuentes.py) — la única diferencia es que aquí el origen
es un fichero local en vez de bytes descargados de MinIO.

IMPORTANTE: esto es el camino de referencia (dataset/ -> staging.* directo),
no el pipeline productivo. Para actualizar una fuente en producción (INE
publica una versión nueva de 69303.csv, etc.) usa la API
(POST /datasets_upload/upload con id_fuente) -> Prefect, no este script.
Ver README.md, sección "Dataset de referencia".

Uso: python scripts/load_tfm_dataset.py
"""
from __future__ import annotations

from pathlib import Path

from src.tasks.staging_fuentes import cargar_fuente_a_staging

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"

# codigo_fuente -> fichero en dataset/
FICHEROS = {
    "tinsa_precios": "tinsa_malaga_andalucia.csv",
    "31106": "31106.csv",
    "31114": "31114.csv",
    "31107": "31107.csv",
    "37706": "37706.csv",
    "2882": "2882.csv",
    "69303": "69303.csv",
    "69301": "69301.csv",
    "69307": "69307.csv",
    "transacciones_libre": "min_Transacciones inmobiliarias de vivienda libre por municipios.XLS",
    "transacciones_segunda_mano": "min_Transacciones inmobiliarias de vivienda de segunda mano por municipios.XLS",
    "transacciones_nueva": "min_Transacciones inmobiliarias de vivienda nueva por municipios.XLS",
    "transacciones_protegida": "min_Transacciones inmobiliarias de vivienda protegida por municipios.XLS",
}


if __name__ == "__main__":
    for codigo_fuente, filename in FICHEROS.items():
        file_bytes = (DATASET_DIR / filename).read_bytes()
        n = cargar_fuente_a_staging(codigo_fuente, file_bytes)
        print(f"staging <- {codigo_fuente} ({filename}): {n} filas")
