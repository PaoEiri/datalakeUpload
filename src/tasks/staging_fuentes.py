"""Dispatcher de carga a staging.* por codigo_fuente, a partir de bytes (MinIO).

Es la versión productiva (Flow 2) de la misma lógica de parseo que
scripts/load_tfm_dataset.py aplica al dataset de referencia local — aquí
opera sobre bytes descargados de MinIO en vez de rutas de fichero, para
poder invocarse desde el flow de Prefect con el storage_key del dataset
vigente de cada fuente. Ver especificacion_carga_datos_TFM.md y
consideraciones_prefect_flows.md.
"""
from __future__ import annotations

import io
import re
from typing import Callable

import pandas as pd
import xlrd
from sqlalchemy import text

from src.db.database import SessionLocal

TRIMESTRE_MES = {1: 1, 2: 4, 3: 7, 4: 10}


# ---------------------------------------------------------------------------
# Tinsa
# ---------------------------------------------------------------------------
def _parse_tinsa(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    return df[["zona", "periodo", "valor", "url"]]


# ---------------------------------------------------------------------------
# Indicadores INE
# ---------------------------------------------------------------------------
def _limpiar_ine(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df.loc[df[col].isin(["nan", "NaN", ""]), col] = None
    return df


def _make_ine_parser(
    encoding: str,
    filtro: Callable[[pd.DataFrame], pd.DataFrame],
    rename: dict[str, str] | None = None,
    drop: list[str] | None = None,
) -> Callable[[bytes], pd.DataFrame]:
    def parser(file_bytes: bytes) -> pd.DataFrame:
        df = pd.read_csv(io.BytesIO(file_bytes), sep=";", encoding=encoding, dtype=str)
        df = _limpiar_ine(df)
        df = filtro(df)
        if drop:
            df = df.drop(columns=drop)
        if rename:
            df = df.rename(columns=rename)
        return df

    return parser


def _filtro_malaga_con_distrito(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        (df["Municipios"].str.strip() == "29067 Málaga")
        & (df["Secciones"].isna() | (df["Secciones"].str.strip() == ""))
    ]


def _filtro_malaga_solo_municipio(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Municipios"].str.strip() == "29067 Málaga"]


def _filtro_malaga_texto(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Municipios"].str.strip() == "Málaga"]


def _filtro_malaga_texto_sexo_total(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["Municipios"].str.strip() == "Málaga") & (df["Sexo"].str.strip() == "Total")]


# ---------------------------------------------------------------------------
# Transacciones (Ministerio) — tabla ancha -> formato largo
# ---------------------------------------------------------------------------
def _make_transacciones_parser(municipio_objetivo: str = "Málaga") -> Callable[[bytes], pd.DataFrame]:
    def parser(file_bytes: bytes) -> pd.DataFrame:
        book = xlrd.open_workbook(file_contents=file_bytes, formatting_info=True)
        sheet = book.sheet_by_index(0)

        def is_bold(row: int, col: int) -> bool:
            xf = book.xf_list[sheet.cell_xf_index(row, col)]
            font = book.font_list[xf.font_index]
            return bool(font.bold)

        header_anio_row = None
        header_trim_row = None
        data_start_row = None
        for r in range(min(20, sheet.nrows)):
            row_vals = [str(sheet.cell_value(r, c)) for c in range(sheet.ncols)]
            if header_anio_row is None and any(v.startswith("Año") for v in row_vals):
                header_anio_row = r
            if any(re.match(r"^\d+º$", v.strip()) for v in row_vals):
                header_trim_row = r
                data_start_row = r + 1
                break
        if header_anio_row is None or header_trim_row is None:
            raise ValueError("No se encontró la cabecera Año/trimestre")

        anio_por_col: dict[int, int | None] = {}
        ultimo_anio = None
        for c in range(3, sheet.ncols):
            v = str(sheet.cell_value(header_anio_row, c))
            if v.startswith("Año"):
                ultimo_anio = int(v.replace("Año", "").strip())
            anio_por_col[c] = ultimo_anio

        col_periodo: dict[int, tuple[int, int]] = {}
        for c in range(3, sheet.ncols):
            trim_cell = str(sheet.cell_value(header_trim_row, c)).strip()
            m = re.match(r"^(\d)º$", trim_cell)
            if m and anio_por_col.get(c):
                col_periodo[c] = (anio_por_col[c], int(m.group(1)))

        provincia_actual = None
        registros = []
        for r in range(data_start_row, sheet.nrows):
            nombre = sheet.cell_value(r, 1)
            if nombre in (None, ""):
                continue
            nombre = str(nombre).strip()

            if is_bold(r, 1):
                provincia_actual = nombre
                continue

            if provincia_actual == municipio_objetivo and nombre == municipio_objetivo:
                for col, (anio, trimestre) in col_periodo.items():
                    valor = sheet.cell_value(r, col)
                    if valor not in (None, ""):
                        registros.append({
                            "municipio": municipio_objetivo,
                            "anio": anio,
                            "trimestre": trimestre,
                            "num_transacciones": int(valor),
                        })

        return pd.DataFrame(registros)

    return parser


# ---------------------------------------------------------------------------
# Registro: codigo_fuente -> (tabla staging destino, parser)
# ---------------------------------------------------------------------------
PARSERS: dict[str, tuple[str, Callable[[bytes], pd.DataFrame]]] = {
    "tinsa_precios": ("tinsa_precios", _parse_tinsa),
    "31106": (
        "ine_renta_persona_hogar",
        _make_ine_parser("latin-1", _filtro_malaga_con_distrito),
    ),
    "31114": (
        "ine_demograficos",
        _make_ine_parser(
            "utf-8-sig",
            _filtro_malaga_con_distrito,
            rename={"Indicadores demográficos": "Indicadores demograficos"},
        ),
    ),
    "31107": (
        "ine_fuente_ingreso",
        _make_ine_parser(
            "utf-8-sig",
            _filtro_malaga_con_distrito,
            rename={
                "Distribución por fuente de ingresos": "Distribucion por fuente de ingresos",
                "% distribucion de fuentes de ingreso": "valor_porcentaje",
            },
        ),
    ),
    "37706": (
        "ine_gini_p80p20",
        _make_ine_parser(
            "utf-8-sig",
            _filtro_malaga_con_distrito,
            rename={
                "Índice de Gini y Distribución de la renta P80/P20": "Indice de Gini y Distribucion de la renta P80/P20"
            },
        ),
    ),
    "2882": (
        "ine_poblacion_sexo",
        _make_ine_parser("latin-1", _filtro_malaga_solo_municipio),
    ),
    "69303": (
        "ine_indicadores_malaga",
        _make_ine_parser("latin-1", _filtro_malaga_texto, drop=["Total Nacional"]),
    ),
    "69301": (
        "ine_demograficos_actualizado",
        _make_ine_parser("latin-1", _filtro_malaga_texto_sexo_total, drop=["Total Nacional"]),
    ),
    "69307": (
        "ine_turismo",
        _make_ine_parser("latin-1", _filtro_malaga_texto, drop=["Total Nacional"]),
    ),
    "transacciones_libre": ("transacciones_libre", _make_transacciones_parser()),
    "transacciones_segunda_mano": ("transacciones_segunda_mano", _make_transacciones_parser()),
    "transacciones_nueva": ("transacciones_nueva", _make_transacciones_parser()),
    "transacciones_protegida": ("transacciones_protegida", _make_transacciones_parser()),
}


def cargar_fuente_a_staging(codigo_fuente: str, file_bytes: bytes) -> int:
    """Parsea file_bytes según codigo_fuente y hace TRUNCATE + INSERT en
    staging.<tabla>. Devuelve el número de filas cargadas."""
    if codigo_fuente not in PARSERS:
        raise ValueError(f"codigo_fuente desconocido: {codigo_fuente}")

    tabla, parser = PARSERS[codigo_fuente]
    df = parser(file_bytes)

    with SessionLocal() as db:
        conn = db.connection()
        conn.execute(text(f"TRUNCATE TABLE staging.{tabla} RESTART IDENTITY"))
        df.to_sql(tabla, con=conn, schema="staging", if_exists="append", index=False)
        db.commit()

    return len(df)
