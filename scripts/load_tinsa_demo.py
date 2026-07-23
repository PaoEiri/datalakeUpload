"""Carga puntual de los CSV reales de Tinsa (repo root) a staging.*, para demo/TFM."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from src.db.database import SessionLocal

TRIMESTRE_MES = {1: 1, 2: 4, 3: 7, 4: 10}
FUENTE = "Tinsa - Precio medio de vivienda (scraping)"

# zona -> (nivel_geografico, tabla destino)
NIVEL_FIJO = {
    "Andalucía": ("AUTONOMICO", "tinsa_precios_andalucia_espana"),
    "España": ("NACIONAL", "tinsa_precios_andalucia_espana"),
}

FILES = [
    "tinsa_malaga.csv",           # Marbella, Vélez Malaga -> municipios
    "tinsa_malaga_ciudad.csv",    # Málaga (municipio) + distritos de Málaga capital
    "tinsa_malaga_andalucia.csv", # Andalucía, España, Málaga (redundante, se descarta)
]


def _periodo_to_parts(periodo: str) -> tuple[int, int, pd.Timestamp]:
    anio_str, trim_str = periodo.strip().split(" ")
    anio = int(anio_str)
    trimestre = int(trim_str.replace("T", ""))
    mes = TRIMESTRE_MES[trimestre]
    return anio, trimestre, pd.Timestamp(year=anio, month=mes, day=1)


def _nivel_y_tabla(zona: str, filename: str) -> tuple[str, str] | None:
    if zona in NIVEL_FIJO:
        if zona == "Málaga" and filename == "tinsa_malaga_andalucia.csv":
            return None
        return NIVEL_FIJO[zona]
    if filename == "tinsa_malaga.csv":
        return ("MUNICIPIO", "tinsa_precios_vivienda")
    if filename == "tinsa_malaga_ciudad.csv":
        nivel = "MUNICIPIO" if zona == "Málaga" else "DISTRITO"
        return (nivel, "tinsa_precios_vivienda")
    if filename == "tinsa_malaga_andalucia.csv" and zona == "Málaga":
        return None  # ya cubierto por tinsa_malaga_ciudad.csv
    return None


def build_rows() -> dict[str, pd.DataFrame]:
    frames: dict[str, list[pd.DataFrame]] = {
        "tinsa_precios_vivienda": [],
        "tinsa_precios_andalucia_espana": [],
    }

    for filename in FILES:
        df = pd.read_csv(filename, encoding="utf-8-sig")
        partes = df["periodo"].apply(_periodo_to_parts)
        df["anio"] = partes.apply(lambda t: t[0])
        df["trimestre"] = partes.apply(lambda t: t[1])
        df["fecha"] = partes.apply(lambda t: t[2])

        destino = df["zona"].apply(lambda z: _nivel_y_tabla(z, filename))
        df = df[destino.notna()].copy()
        df["nivel_geografico"] = destino[destino.notna()].apply(lambda t: t[0])
        df["tabla"] = destino[destino.notna()].apply(lambda t: t[1])
        df["fuente"] = FUENTE

        for tabla, grupo in df.groupby("tabla"):
            frames[tabla].append(
                grupo[["zona", "nivel_geografico", "anio", "trimestre", "fecha", "valor", "fuente"]]
            )

    return {tabla: pd.concat(dfs, ignore_index=True) for tabla, dfs in frames.items() if dfs}


if __name__ == "__main__":
    tablas = build_rows()
    with SessionLocal() as db:
        conn = db.connection()
        for tabla, df_clean in tablas.items():
            conn.execute(text(f"DELETE FROM staging.{tabla} WHERE fuente = :fuente"), {"fuente": FUENTE})
            df_clean.to_sql(tabla, con=conn, schema="staging", if_exists="append", index=False)
            print(f"staging.{tabla}: {len(df_clean)} filas ({sorted(df_clean['nivel_geografico'].unique())})")
        db.commit()
