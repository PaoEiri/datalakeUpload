"""Carga las 13 fuentes reales de dataset/ a staging.*, para el dataset de
referencia del TFM. Reutiliza los mismos parsers que el pipeline productivo
(src/tasks/staging_fuentes.py) — la única diferencia es que aquí el origen
es un fichero local en vez de bytes descargados de MinIO.

IMPORTANTE: esto es el camino de referencia (dataset/ -> staging.* directo),
no el pipeline productivo. Para actualizar una fuente en producción (INE
publica una versión nueva de 69303.csv, etc.) usa la API
(POST /datasets_upload/upload con id_fuente) -> Prefect, no este script.
Ver README.md, sección "Dataset de referencia".

Solo para la carga inicial sobre una base vacía. Los nombres de FICHEROS son
los del snapshot original del TFM y no siguen al catálogo: si una fuente ya
tiene una versión subida por la API (fuentes_registradas.id_dataset_actual),
ejecutar este script sobrescribiría staging con datos más antiguos que los
vigentes. Por eso se niega a ejecutarse en ese caso salvo con --force. Para
recargar la versión vigente de una fuente usa
POST /fuentes_registradas/{id_fuente}/reprocesar o
flows/04_staging_manual.py <id_fuente>.

Uso: python scripts/load_tfm_dataset.py [--force]
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

from src.db.database import SessionLocal
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
    "69333": "69333.csv",
    "69330": "69330.csv",
    "31111": "31111.csv",
    "transacciones_libre": "min_Transacciones inmobiliarias de vivienda libre por municipios.XLS",
    "transacciones_segunda_mano": "min_Transacciones inmobiliarias de vivienda de segunda mano por municipios.XLS",
    "transacciones_nueva": "min_Transacciones inmobiliarias de vivienda nueva por municipios.XLS",
    "transacciones_protegida": "min_Transacciones inmobiliarias de vivienda protegida por municipios.XLS",
}


def fuentes_con_version_en_catalogo() -> list[tuple[str, str]]:
    with SessionLocal() as db:
        rows = db.execute(text(
            "SELECT f.codigo_fuente, d.original_filename "
            "FROM fuentes_registradas f "
            "JOIN datasets_upload d ON d.id = f.id_dataset_actual "
            "ORDER BY f.codigo_fuente"
        )).all()
    return [(r[0], r[1]) for r in rows]


if __name__ == "__main__":
    if "--force" not in sys.argv:
        vigentes = fuentes_con_version_en_catalogo()
        if vigentes:
            print("Abortado: estas fuentes ya tienen una versión vigente cargada por la API,")
            print("que este script sobrescribiría con el snapshot original de dataset/:")
            for codigo_fuente, filename in vigentes:
                print(f"  - {codigo_fuente}: {filename}")
            print("Para recargar la versión vigente: POST /fuentes_registradas/{id_fuente}/reprocesar")
            print("o flows/04_staging_manual.py <id_fuente>. Usa --force para cargar el snapshot igualmente.")
            sys.exit(1)

    for codigo_fuente, filename in FICHEROS.items():
        file_bytes = (DATASET_DIR / filename).read_bytes()
        n = cargar_fuente_a_staging(codigo_fuente, file_bytes)
        print(f"staging <- {codigo_fuente} ({filename}): {n} filas")
