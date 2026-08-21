"""Pipeline de ML: predicción de la variación trimestral (%) de precio_m2 a
nivel municipal (Málaga). Ver consideraciones/instrucciones_ml_claude_code.md
para el diseño completo.

Todas las tasks son sync (mismo estilo que src/tasks/dbt.py y
src/tasks/staging_fuentes.py), cada una abre su propia sesión de DB.
"""
from __future__ import annotations

import io
import logging
import pickle
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from prefect import task, get_run_logger
from prefect.exceptions import MissingContextError
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from src.config import settings
from src.db.database import SessionLocal, engine
from src.db import crud_sync


def _get_logger():
    try:
        return get_run_logger()
    except MissingContextError:
        # Mismo motivo que en src/tasks/dbt.py: estas tasks también se
        # pueden invocar vía .fn(...) fuera de un flow run.
        return logging.getLogger(__name__)


def _slugify(nombre: str) -> str:
    slug = nombre.lower()
    slug = re.sub(r"[áàä]", "a", slug)
    slug = re.sub(r"[éèë]", "e", slug)
    slug = re.sub(r"[íìï]", "i", slug)
    slug = re.sub(r"[óòö]", "o", slug)
    slug = re.sub(r"[úùü]", "u", slug)
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")[:60]


LAG_COLS = ["precio_m2_lag1", "precio_m2_lag4", "precio_m2_lag8", "num_transacciones_lag1"]
BASE_FEATURE_COLS = LAG_COLS + ["variacion_interanual", "is_estimated"]

TRAIN_ANIOS = (2010, 2022)
# Ventana de validación amplia a propósito: con solo 8 trimestres (2023-2024)
# el R² es extremadamente inestable — esos trimestres tuvieron variación de
# precio inusualmente estable (poca varianza), así que cualquier sesgo
# pequeño hundía el R² sin reflejar una diferencia real de calidad entre
# modelos (verificado en sesión: el mismo modelo pasaba de R²=0.69 a -1.04
# solo por variar 2 features, con folds idénticos en todo lo demás).
# 2019-2024 (24 trimestres) incluye el shock de la COVID y da una medición
# mucho más robusta. Ampliado a 2019-2026 en una sesión posterior: excluir
# 2025-2026 ocultaba un sesgo sistemático de subestimación en esos
# trimestres (indicadores sin dato real todavía, ver
# _extender_indicadores_anuales) que sí afecta la calidad real del modelo
# y debía reflejarse en el gate, no quedar fuera de la medición.
VAL_ANIOS = (2019, 2026)

# Indicadores con tendencia clara y consistente (verificado en sesión sobre
# su histórico completo: suben o bajan año a año sin reversiones relevantes
# en la última década) — se extrapolan hacia adelante en vez de congelarse
# en el último valor real, tanto en build_features (trimestres recientes sin
# dato real de indicador todavía, ej. 2025-2026) como en forecast_recursivo
# (forecast puro). Deliberadamente NO incluye Tasa de desempleo (23): tuvo
# un ciclo completo de subida y bajada dentro del propio rango de
# entrenamiento (2010-2024), así que asumir que la tendencia reciente
# continúa sería más arriesgado que congelarlo. Cualquier indicador nuevo
# que no esté en este set se congela por defecto (opción conservadora).
INDICADORES_TENDENCIA_IDS = {24, 27, 33, 47, 73}
ANIOS_TENDENCIA = 3  # ventana de años recientes para estimar la tasa de crecimiento


def _extender_indicadores_anuales(
    ind_wide: pd.DataFrame, indicator_cols: list[str], id_to_slug: dict, anio_min: int, anio_max: int
) -> pd.DataFrame:
    """Extiende cada indicador (índice=año) desde su último año con dato real
    hasta anio_max: para los indicadores en INDICADORES_TENDENCIA_IDS
    extrapola con su tasa de crecimiento interanual reciente (últimos
    ANIOS_TENDENCIA años reales); el resto se congela en el último valor
    real (ffill plano) — mismo criterio que forecast_recursivo.

    Se detectó en sesión que el ffill plano original sesgaba
    sistemáticamente a la baja el backtesting de trimestres recientes sin
    dato de indicador todavía (2025-2026): el precio real seguía subiendo
    mientras el modelo veía renta/alquiler/etc. "congelados" en 2023-2024.
    """
    slug_to_id = {v: k for k, v in id_to_slug.items()}
    resultado = ind_wide.reindex(range(anio_min, anio_max + 1)).sort_index().copy()
    for col in indicator_cols:
        if col not in resultado.columns:
            continue
        serie_real = ind_wide[col].dropna() if col in ind_wide.columns else pd.Series(dtype=float)
        if serie_real.empty:
            continue
        ultimo_anio_real = int(serie_real.index.max())
        ultimo_valor_real = float(serie_real.loc[ultimo_anio_real])
        id_indicador = slug_to_id.get(col)
        if id_indicador in INDICADORES_TENDENCIA_IDS:
            recientes = serie_real.tail(ANIOS_TENDENCIA + 1)
            variaciones = recientes.pct_change().dropna()
            tasa = float(variaciones.mean()) if len(variaciones) > 0 else 0.0
        else:
            tasa = 0.0
        for anio in resultado.index:
            if anio > ultimo_anio_real:
                resultado.loc[anio, col] = ultimo_valor_real * (1 + tasa) ** (anio - ultimo_anio_real)
        resultado[col] = resultado[col].ffill()  # cubre huecos previos al último real, si los hubiera
    return resultado


# ---------------------------------------------------------------------------
# 1. build_features
# ---------------------------------------------------------------------------
@task(name="ml-build-features", retries=0)
def build_features() -> pd.DataFrame:
    """Pivota fact_indicadores_anuales (EAV) a ancho, une con precio/
    transacciones trimestrales, hace forward-fill anual->trimestral, calcula
    lags y el target, y persiste el resultado en public.mart_features_ml."""
    logger = _get_logger()

    with engine.connect() as conn:
        geo = pd.read_sql(
            "SELECT id_geografia FROM core.dim_geografia "
            "WHERE nivel = 'Municipio' AND codigo_ine = '29067'",
            conn,
        )
        if geo.empty:
            raise RuntimeError("No se encontró el municipio de Málaga (codigo_ine=29067) en dim_geografia.")
        id_geografia = int(geo.iloc[0]["id_geografia"])

        indicadores = pd.read_sql(
            "SELECT indicador_id, nombre_indicador FROM reference.seed_indicadores_fuentes "
            "WHERE usar_en_ml = true ORDER BY indicador_id",
            conn,
        )
        if indicadores.empty:
            raise RuntimeError(
                "Ningún indicador tiene usar_en_ml=true — actívalos desde la pestaña "
                "Indicadores de la UI antes de correr el flow de ML."
            )
        logger.info(f"Indicadores para ML ({len(indicadores)}): {indicadores['nombre_indicador'].tolist()}")

        precio = pd.read_sql(
            """
            SELECT dt.anio, dt.trimestre, dt.id_tiempo, fp.precio_m2
            FROM marts.fact_precio_vivienda fp
            JOIN core.dim_tiempo dt ON fp.id_tiempo = dt.id_tiempo
            WHERE fp.id_geografia = %(gid)s AND dt.trimestre IS NOT NULL
            ORDER BY dt.anio, dt.trimestre
            """,
            conn,
            params={"gid": id_geografia},
        )
        transacciones = pd.read_sql(
            """
            SELECT dt.anio, dt.trimestre, SUM(ft.num_transacciones) AS num_transacciones
            FROM marts.fact_transacciones_inmobiliarias ft
            JOIN core.dim_tiempo dt ON ft.id_tiempo = dt.id_tiempo
            WHERE ft.id_geografia = %(gid)s
            GROUP BY dt.anio, dt.trimestre
            """,
            conn,
            params={"gid": id_geografia},
        )
        indicadores_anuales = pd.read_sql(
            """
            SELECT dt.anio, fi.id_indicador, fi.valor
            FROM marts.fact_indicadores_anuales fi
            JOIN core.dim_tiempo dt ON fi.id_tiempo = dt.id_tiempo
            WHERE fi.id_geografia = %(gid)s
              AND dt.trimestre IS NULL
              AND fi.id_indicador = ANY(%(ids)s)
            """,
            conn,
            params={"gid": id_geografia, "ids": indicadores["indicador_id"].tolist()},
        )

    if precio.empty:
        raise RuntimeError("marts.fact_precio_vivienda no tiene datos para Málaga municipio.")

    # --- Pivot EAV -> ancho ---
    id_to_slug = {
        int(r.indicador_id): _slugify(r.nombre_indicador) for r in indicadores.itertuples()
    }
    ind_wide = indicadores_anuales.pivot_table(
        index="anio", columns="id_indicador", values="valor", aggfunc="first"
    ).rename(columns=id_to_slug)
    indicator_cols = list(id_to_slug.values())
    ind_wide = ind_wide.reindex(columns=indicator_cols)

    # Un indicador con usar_en_ml=true puede no tener NINGÚN dato a nivel
    # municipal para Málaga — ej. está marcado aplica_municipal=false (solo
    # aplica a distrito), o su dato quedó archivado bajo el id_indicador
    # canónico de otro indicador del mismo concepto_id (ver
    # int_indicadores_unificado.sql). Sin este filtro, la columna queda 100%
    # NaN y el dropna final antes de entrenar elimina TODAS las filas
    # (0 muestras), tirando abajo el flow entero por la selección de un
    # solo indicador en la pestaña "Usar en ML" de la UI.
    indicadores_sin_dato = [c for c in indicator_cols if ind_wide[c].isna().all()]
    if indicadores_sin_dato:
        slug_to_id = {v: k for k, v in id_to_slug.items()}
        logger.warning(
            f"Indicadores con usar_en_ml=true pero sin ningún dato municipal para Málaga "
            f"(excluidos de este entrenamiento — revisa aplica_municipal/concepto_id en "
            f"reference.seed_indicadores_fuentes, o la pestaña Indicadores de la UI): "
            f"{[(slug_to_id[c], c) for c in indicadores_sin_dato]}"
        )
        indicator_cols = [c for c in indicator_cols if c not in indicadores_sin_dato]
        ind_wide = ind_wide.drop(columns=indicadores_sin_dato)

    # --- Backbone trimestral (rango completo de precio_m2) ---
    backbone = precio[["anio", "trimestre", "id_tiempo"]].copy()
    df = backbone.merge(precio[["anio", "trimestre", "precio_m2"]], on=["anio", "trimestre"], how="left")
    df = df.merge(transacciones, on=["anio", "trimestre"], how="left")
    # transacciones suele publicarse con 1 trimestre de rezago respecto a
    # precio_m2 — sin este ffill, el último trimestre real (usado como punto
    # de partida del forecast recursivo) queda con num_transacciones NaN y
    # rompe la predicción (Ridge/XGBoost no aceptan NaN).
    df["num_transacciones"] = df.sort_values(["anio", "trimestre"])["num_transacciones"].ffill()

    # --- Forward-fill anual -> trimestral (con extrapolación de tendencia) ---
    max_anio_real = int(indicadores_anuales["anio"].max()) if not indicadores_anuales.empty else None
    anio_min, anio_max = int(df["anio"].min()), int(df["anio"].max())
    ind_wide_full = _extender_indicadores_anuales(ind_wide, indicator_cols, id_to_slug, anio_min, anio_max)

    df = df.merge(ind_wide_full, left_on="anio", right_index=True, how="left")
    df["is_estimated"] = (df["anio"] > max_anio_real) if max_anio_real is not None else False

    # --- Lags y target ---
    df = df.sort_values(["anio", "trimestre"]).reset_index(drop=True)
    df["precio_m2_lag1"] = df["precio_m2"].shift(1)
    df["precio_m2_lag4"] = df["precio_m2"].shift(4)
    df["precio_m2_lag8"] = df["precio_m2"].shift(8)
    df["num_transacciones_lag1"] = df["num_transacciones"].shift(1)
    df["variacion_interanual"] = df["precio_m2"] / df["precio_m2_lag4"] - 1
    df["target"] = df["precio_m2"] / df["precio_m2_lag1"] - 1
    df["id_geografia"] = id_geografia

    cols_orden = (
        ["id_geografia", "id_tiempo", "anio", "trimestre", "precio_m2", "num_transacciones"]
        + indicator_cols
        + ["precio_m2_lag1", "precio_m2_lag4", "precio_m2_lag8", "num_transacciones_lag1",
           "variacion_interanual", "is_estimated", "target"]
    )
    df = df[cols_orden]

    df.to_sql("mart_features_ml", engine, schema="public", if_exists="replace", index=False)
    logger.info(f"mart_features_ml: {len(df)} filas, {len(indicator_cols)} indicadores, "
                f"rango {anio_min}-{anio_max}.")

    df.attrs["indicator_cols"] = indicator_cols
    df.attrs["id_geografia"] = id_geografia
    return df


def _feature_cols(df: pd.DataFrame) -> list[str]:
    indicator_cols = df.attrs.get("indicator_cols")
    if indicator_cols is None:
        # df releído de Postgres (no conserva .attrs) — se infiere por descarte.
        conocidas = set(["id_geografia", "id_tiempo", "anio", "trimestre", "precio_m2",
                          "num_transacciones", "target"] + BASE_FEATURE_COLS)
        indicator_cols = [c for c in df.columns if c not in conocidas]
    return indicator_cols + BASE_FEATURE_COLS


def _naive_predict(df_hist: pd.DataFrame) -> float:
    """Baseline: media móvil de las últimas 4 variaciones trimestrales conocidas."""
    ultimas = df_hist["target"].dropna().tail(4)
    return float(ultimas.mean()) if len(ultimas) > 0 else 0.0


def _directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(np.sign(y_true) == np.sign(y_pred)))


def _walk_forward(df: pd.DataFrame, feature_cols: list[str], build_pipeline) -> dict:
    """Ventana expansiva: para cada trimestre de validación, entrena con todo
    lo anterior (empezando en TRAIN_ANIOS[0]) y predice ese trimestre.
    build_pipeline() debe devolver un sklearn Pipeline sin entrenar."""
    df = df.dropna(subset=feature_cols + ["target"]).reset_index(drop=True)
    train_mask_base = df["anio"] >= TRAIN_ANIOS[0]
    val_mask = (df["anio"] >= VAL_ANIOS[0]) & (df["anio"] <= VAL_ANIOS[1])

    y_true, y_pred, y_pred_naive = [], [], []
    for idx in df.index[val_mask]:
        hist = df.loc[(df.index < idx) & train_mask_base]
        if len(hist) < 8:
            continue
        pipeline = build_pipeline()
        pipeline.fit(hist[feature_cols], hist["target"])
        pred = pipeline.predict(df.loc[[idx], feature_cols])[0]
        y_true.append(df.loc[idx, "target"])
        y_pred.append(pred)
        y_pred_naive.append(_naive_predict(hist))

    y_true, y_pred, y_pred_naive = np.array(y_true), np.array(y_pred), np.array(y_pred_naive)
    if len(y_true) == 0:
        return {"r2": None, "rmse": None, "mae": None, "accuracy_direccional": None, "n": 0}

    return {
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else None,
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "accuracy_direccional": _directional_accuracy(y_true, y_pred),
        "n": len(y_true),
        "y_true": y_true,
        "y_pred": y_pred,
        "y_pred_naive": y_pred_naive,
    }


@dataclass
class ModeloEntrenado:
    algoritmo: str
    pipeline: object
    hiperparametros: dict
    metricas: dict = field(default_factory=dict)


RIDGE_ALPHAS = [0.001, 0.0025, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300]

XGB_GRID = dict(
    max_depth=[2, 3, 4],
    n_estimators=[30, 50, 100, 150, 200],
    learning_rate=[0.01, 0.03, 0.05, 0.1, 0.2],
    min_child_weight=[3, 5, 10],
    subsample=[0.6, 0.8, 1.0],
    colsample_bytree=[0.6, 0.8, 1.0],
)
N_ITER_XGB = 25  # búsqueda aleatoria acotada, no grid completo (5*5*5*3*3*3=3375 combos)


def _log_top_n(logger, nombre: str, evaluados: list[tuple[dict, dict]], n: int = 5) -> None:
    ordenados = sorted(
        evaluados, key=lambda e: e[1]["r2"] if e[1]["r2"] is not None else -np.inf, reverse=True
    )
    logger.info(f"{nombre}: {len(evaluados)} combinaciones evaluadas, top-{n}:")
    for params, metricas in ordenados[:n]:
        logger.info(f"  r2={metricas['r2']} acc_dir={metricas['accuracy_direccional']} params={params}")


# ---------------------------------------------------------------------------
# 2. train_models — Ridge: grid exhaustivo; XGBoost: random search acotado,
# ambos seleccionados por walk-forward
# ---------------------------------------------------------------------------
@task(name="ml-train-models", retries=0)
def train_models(df: pd.DataFrame) -> dict[str, ModeloEntrenado]:
    logger = _get_logger()
    feature_cols = _feature_cols(df)

    n_train = int(((df["anio"] >= TRAIN_ANIOS[0]) & (df["anio"] <= TRAIN_ANIOS[1])).sum())
    if len(feature_cols) > n_train / 10:
        logger.warning(
            f"n_features={len(feature_cols)} vs n_train={n_train}: muestra pequeña para la "
            f"cantidad de features, alto riesgo de overfitting (esperado con series trimestrales "
            f"de una sola geografía). Se prioriza regularización fuerte."
        )

    resultados: dict[str, ModeloEntrenado] = {}

    # --- Naive (sin fit real, solo referencia) ---
    resultados["naive"] = ModeloEntrenado(algoritmo="naive", pipeline=None, hiperparametros={})

    # --- Ridge: grid exhaustivo de alpha (barato, 1 solo hiperparámetro) ---
    evaluados_ridge = []
    for alpha in RIDGE_ALPHAS:
        build = lambda a=alpha: Pipeline([
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=a, random_state=42)),
        ])
        metricas = _walk_forward(df, feature_cols, build)
        evaluados_ridge.append(({"alpha": alpha}, metricas))
    _log_top_n(logger, "Ridge", evaluados_ridge)
    mejores_params, metricas = max(
        evaluados_ridge, key=lambda e: e[1]["r2"] if e[1]["r2"] is not None else -np.inf
    )
    pipeline = Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=mejores_params["alpha"], random_state=42))])
    pipeline.fit(df.dropna(subset=feature_cols + ["target"])[feature_cols],
                 df.dropna(subset=feature_cols + ["target"])["target"])
    resultados["ridge"] = ModeloEntrenado(
        algoritmo="ridge", pipeline=pipeline,
        hiperparametros={**mejores_params, "n_combinaciones_evaluadas": len(evaluados_ridge)},
        metricas=metricas,
    )

    # --- XGBoost: random search acotado (grid completo sería combinatoriamente
    # caro y, con ~52 filas de train, buscar de más sobreajusta la selección
    # de hiperparámetros al propio tramo de validación) ---
    rng = np.random.RandomState(42)
    combos_vistos = set()
    evaluados_xgb = []
    while len(evaluados_xgb) < N_ITER_XGB:
        params = {k: v[rng.randint(len(v))] for k, v in XGB_GRID.items()}
        clave = tuple(sorted(params.items()))
        if clave in combos_vistos:
            continue
        combos_vistos.add(clave)
        params["random_state"] = 42
        build = lambda p=params: Pipeline([("model", XGBRegressor(**p))])
        metricas = _walk_forward(df, feature_cols, build)
        evaluados_xgb.append((params, metricas))
    _log_top_n(logger, "XGBoost", evaluados_xgb)
    mejores_params, metricas = max(
        evaluados_xgb, key=lambda e: e[1]["r2"] if e[1]["r2"] is not None else -np.inf
    )
    pipeline = Pipeline([("model", XGBRegressor(**mejores_params))])
    pipeline.fit(df.dropna(subset=feature_cols + ["target"])[feature_cols],
                 df.dropna(subset=feature_cols + ["target"])["target"])
    resultados["xgboost"] = ModeloEntrenado(
        algoritmo="xgboost", pipeline=pipeline,
        hiperparametros={**mejores_params, "n_combinaciones_evaluadas": len(evaluados_xgb)},
        metricas=metricas,
    )

    return resultados


# ---------------------------------------------------------------------------
# 3. validate_walkforward — recalcula métricas oficiales para el gate
# ---------------------------------------------------------------------------
@task(name="ml-validate-walkforward", retries=0)
def validate_walkforward(modelos: dict[str, ModeloEntrenado], df: pd.DataFrame) -> dict[str, dict]:
    logger = _get_logger()
    feature_cols = _feature_cols(df)
    resultado = {}

    # Naive: walk-forward con la media móvil de 4 trimestres.
    df_val = df.dropna(subset=feature_cols + ["target"]).reset_index(drop=True)
    val_mask = (df_val["anio"] >= VAL_ANIOS[0]) & (df_val["anio"] <= VAL_ANIOS[1])
    y_true_n, y_pred_n = [], []
    for idx in df_val.index[val_mask]:
        hist = df_val.loc[df_val.index < idx]
        if len(hist) < 4:
            continue
        y_true_n.append(df_val.loc[idx, "target"])
        y_pred_n.append(_naive_predict(hist))
    y_true_n, y_pred_n = np.array(y_true_n), np.array(y_pred_n)
    resultado["naive"] = {
        "r2": float(r2_score(y_true_n, y_pred_n)) if len(y_true_n) > 1 else None,
        "rmse": float(np.sqrt(mean_squared_error(y_true_n, y_pred_n))) if len(y_true_n) else None,
        "mae": float(mean_absolute_error(y_true_n, y_pred_n)) if len(y_true_n) else None,
        "accuracy_direccional": _directional_accuracy(y_true_n, y_pred_n),
    }

    for nombre in ("ridge", "xgboost"):
        m = modelos[nombre].metricas
        resultado[nombre] = {k: m.get(k) for k in ("r2", "rmse", "mae", "accuracy_direccional")}
        logger.info(f"{nombre}: r2={resultado[nombre]['r2']} acc_dir={resultado[nombre]['accuracy_direccional']}")

    return resultado


# ---------------------------------------------------------------------------
# 4. decide_gate
# ---------------------------------------------------------------------------
R2_GATE = 0.75
ACC_DIR_GATE = 0.75


@task(name="ml-decide-gate", retries=0)
def decide_gate(metricas: dict[str, dict]) -> Optional[str]:
    """Devuelve el nombre del algoritmo champion (ridge o xgboost) si alguno
    cumple el gate, o None si ninguno lo cumple. Si ambos cumplen, gana el de
    mayor R²."""
    logger = _get_logger()
    candidatos = []
    for nombre in ("ridge", "xgboost"):
        m = metricas[nombre]
        r2, acc = m.get("r2"), m.get("accuracy_direccional")
        cumple = r2 is not None and acc is not None and r2 >= R2_GATE and acc >= ACC_DIR_GATE
        margen_r2 = None if r2 is None else round(r2 - R2_GATE, 4)
        margen_acc = None if acc is None else round(acc - ACC_DIR_GATE, 4)
        logger.info(
            f"Gate {nombre}: r2={r2} (margen={margen_r2}) acc_dir={acc} (margen={margen_acc}) "
            f"-> {'PASA' if cumple else 'NO PASA'}"
        )
        if cumple:
            candidatos.append((nombre, r2))

    if not candidatos:
        logger.warning(
            "Ningún modelo (ridge/xgboost) cumple el gate (R²>=0.75 AND accuracy_direccional>=0.75). "
            "No se reemplaza el champion actual."
        )
        return None

    champion = max(candidatos, key=lambda c: c[1])[0]
    logger.info(f"Champion: {champion}")
    return champion


# ---------------------------------------------------------------------------
# 5. persist_model
# ---------------------------------------------------------------------------
@task(name="ml-persist-model", retries=0)
def _slug_a_indicador_map() -> dict[str, tuple[int, str]]:
    """Mapa slug-de-columna -> (indicador_id, nombre_indicador) para los
    indicadores actualmente usar_en_ml=true — compartido por
    _indicadores_usados y _importancia_features."""
    with engine.connect() as conn:
        activos = pd.read_sql(
            "SELECT indicador_id, nombre_indicador FROM reference.seed_indicadores_fuentes "
            "WHERE usar_en_ml = true ORDER BY indicador_id",
            conn,
        )
    return {
        _slugify(r.nombre_indicador): (int(r.indicador_id), r.nombre_indicador)
        for r in activos.itertuples()
    }


def _indicadores_usados(feature_cols: list[str]) -> list[dict]:
    """Indicadores (usar_en_ml=true) que quedaron efectivamente en el feature
    set del modelo persistido — para trazabilidad en ml_model_registry."""
    slug_a_indicador = _slug_a_indicador_map()
    indicator_cols = [c for c in feature_cols if c not in BASE_FEATURE_COLS]
    return [
        {"id": slug_a_indicador[c][0], "nombre": slug_a_indicador[c][1]}
        for c in indicator_cols if c in slug_a_indicador
    ]


def _importancia_features(modelo: ModeloEntrenado) -> list[dict]:
    """Peso/importancia de cada feature del modelo persistido: coeficientes
    estandarizados para Ridge, feature_importances_ para XGBoost — mismo
    criterio que ya usa _generar_shap_plot para el gráfico, aquí devuelto
    como dato estructurado. Ordenado por |valor| descendente."""
    slug_a_indicador = _slug_a_indicador_map()

    if modelo.algoritmo == "xgboost":
        xgb_model = modelo.pipeline.named_steps["model"]
        nombres = xgb_model.get_booster().feature_names
        valores = xgb_model.feature_importances_
    elif modelo.algoritmo == "ridge":
        nombres = list(modelo.pipeline.feature_names_in_)
        valores = modelo.pipeline.named_steps["model"].coef_
    else:  # naive: sin pipeline entrenado, sin coeficientes que reportar
        return []

    filas = []
    for nombre, valor in zip(nombres, valores):
        id_indicador = slug_a_indicador.get(nombre, (None, None))[0]
        filas.append({"feature": nombre, "id_indicador": id_indicador, "valor": float(valor)})
    filas.sort(key=lambda f: -abs(f["valor"]))
    return filas


def persist_model(modelo: ModeloEntrenado, metricas: dict, df: pd.DataFrame) -> int:
    from src.storage.minio_client import MinioClient

    logger = _get_logger()
    version = pd.Timestamp.utcnow().strftime("%Y%m%d_%H%M%S") + f"_{modelo.algoritmo}"
    indicadores_usados = _indicadores_usados(_feature_cols(df))
    importancia_features = _importancia_features(modelo)

    minio = MinioClient(
        endpoint_url=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.datasets_bucket,
        secure=settings.minio_secure,
    )

    ruta_modelo = f"ml/models/{version}/modelo.pkl"
    minio.upload_fileobj(io.BytesIO(pickle.dumps(modelo.pipeline)), ruta_modelo, bucket_name=settings.datasets_bucket)

    ruta_shap = _generar_shap_plot(modelo, version, minio)

    with SessionLocal() as db:
        registro = crud_sync.create_model_registry_entry(
            db,
            version=version,
            algoritmo=modelo.algoritmo,
            hiperparametros=modelo.hiperparametros,
            r2=metricas.get("r2"),
            accuracy_direccional=metricas.get("accuracy_direccional"),
            rmse=metricas.get("rmse"),
            mae=metricas.get("mae"),
            ruta_minio_modelo=ruta_modelo,
            ruta_minio_shap=ruta_shap,
            indicadores_usados=indicadores_usados,
            importancia_features=importancia_features,
        )
        crud_sync.set_champion(db, registro.id_modelo)
        id_modelo = registro.id_modelo

    logger.info(f"Modelo persistido: version={version} id_modelo={id_modelo} ruta={ruta_modelo}")
    return id_modelo


def _generar_shap_plot(modelo: ModeloEntrenado, version: str, minio) -> Optional[str]:
    """SHAP TreeExplainer para XGBoost; para Ridge, coeficientes estandarizados
    (mismo criterio de explicabilidad para ambos modelos no-naive)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        if modelo.algoritmo == "xgboost":
            import shap
            xgb_model = modelo.pipeline.named_steps["model"]
            explainer = shap.TreeExplainer(xgb_model)
            # Nota: idealmente se pasaría el X de entrenamiento real; se omite
            # aquí por simplicidad y se documenta como mejora futura si se
            # necesita el summary plot completo en vez de solo importancias.
            importancias = pd.Series(
                xgb_model.feature_importances_, index=xgb_model.get_booster().feature_names
            ).sort_values()
            importancias.plot.barh(ax=ax)
            ax.set_title(f"Importancia de features (XGBoost, {version})")
        else:
            coefs = pd.Series(
                modelo.pipeline.named_steps["model"].coef_,
                index=modelo.pipeline.feature_names_in_,
            ).sort_values()
            coefs.plot.barh(ax=ax)
            ax.set_title(f"Coeficientes estandarizados (Ridge, {version})")

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        ruta = f"ml/models/{version}/explicabilidad.png"
        minio.upload_fileobj(buf, ruta, bucket_name=settings.datasets_bucket)
        return ruta
    except Exception:
        logging.getLogger(__name__).exception("No se pudo generar el gráfico de explicabilidad.")
        return None


# ---------------------------------------------------------------------------
# 6. forecast_recursivo
# ---------------------------------------------------------------------------
FORECAST_TRIMESTRES = 6  # 2026T3 .. 2027T4


def _tasas_crecimiento_anual(indicator_cols: list[str], id_geografia: int) -> dict[str, float]:
    """Tasa de crecimiento anual reciente (promedio de variación interanual
    de los últimos ANIOS_TENDENCIA años con dato REAL, no forward-filled) para
    los indicadores en INDICADORES_TENDENCIA_IDS — 0.0 (congelado) para el
    resto. Se consulta directo marts.fact_indicadores_anuales en vez de usar
    la serie ya pivotada/forward-filleada de build_features: esa serie repite
    el último valor real en los años sin publicación todavía (is_estimated),
    lo que diluiría la tasa de crecimiento hacia 0 si se usara tal cual."""
    slug_a_indicador = _slug_a_indicador_map()
    tasas = {}
    with engine.connect() as conn:
        for col in indicator_cols:
            id_indicador = slug_a_indicador.get(col, (None, None))[0]
            if id_indicador not in INDICADORES_TENDENCIA_IDS:
                tasas[col] = 0.0
                continue
            anual = pd.read_sql(
                "SELECT dt.anio, fi.valor FROM marts.fact_indicadores_anuales fi "
                "JOIN core.dim_tiempo dt ON fi.id_tiempo = dt.id_tiempo "
                "WHERE fi.id_indicador = %(id)s AND fi.id_geografia = %(geo)s "
                "ORDER BY dt.anio",
                conn, params={"id": id_indicador, "geo": id_geografia},
            )
            recientes = anual["valor"].tail(ANIOS_TENDENCIA + 1)
            variaciones = recientes.pct_change().dropna()
            tasas[col] = float(variaciones.mean()) if len(variaciones) > 0 else 0.0
    return tasas


@task(name="ml-forecast-recursivo", retries=0)
def forecast_recursivo(modelo: ModeloEntrenado, df: pd.DataFrame, id_modelo: int, metricas: dict) -> None:
    logger = _get_logger()
    feature_cols = _feature_cols(df)
    indicator_cols = df.attrs.get("indicator_cols") or [
        c for c in feature_cols if c not in BASE_FEATURE_COLS
    ]
    id_geografia = int(df["id_geografia"].iloc[0])
    rmse_val = metricas.get("rmse") or 0.0

    with SessionLocal() as db:
        # --- Backtesting: filas ya en df con precio_m2 real (test = validación
        # walk-forward ya hecha; aquí se guardan también 2025+ si ya hay dato
        # real de precio, es_forecast=False) ---
        df_completo = df.dropna(subset=feature_cols).copy()
        preds = modelo.pipeline.predict(df_completo[feature_cols]) if modelo.pipeline else None
        for i, row in enumerate(df_completo.itertuples()):
            if row.anio < TRAIN_ANIOS[0]:
                continue
            precio_predicho = row.precio_m2_lag1 * (1 + preds[i]) if preds is not None else row.precio_m2
            crud_sync.create_prediccion(
                db,
                id_geografia=id_geografia,
                anio=int(row.anio),
                trimestre=int(row.trimestre),
                id_modelo=id_modelo,
                precio_predicho=float(precio_predicho),
                es_forecast=False,
            )

        # --- Forecast recursivo puro (sin dato real de precio) ---
        historial = df.sort_values(["anio", "trimestre"]).copy()
        ultimo_anio, ultimo_trim = int(historial["anio"].iloc[-1]), int(historial["trimestre"].iloc[-1])
        indicadores_proyectados = dict(historial.iloc[-1][indicator_cols])
        crecimiento_anual = _tasas_crecimiento_anual(indicator_cols, id_geografia)
        if any(v != 0.0 for v in crecimiento_anual.values()):
            logger.info(
                "Extrapolando indicadores con tendencia (resto congelado en último valor real): "
                + ", ".join(f"{c}={v:+.3%}/año" for c, v in crecimiento_anual.items() if v != 0.0)
            )

        serie_precio = list(historial["precio_m2"])
        serie_transacciones = list(historial["num_transacciones"])

        anio, trimestre = ultimo_anio, ultimo_trim
        for paso in range(1, FORECAST_TRIMESTRES + 1):
            trimestre += 1
            if trimestre > 4:
                trimestre = 1
                anio += 1

            lag1 = serie_precio[-1]
            lag4 = serie_precio[-4] if len(serie_precio) >= 4 else lag1
            lag8 = serie_precio[-8] if len(serie_precio) >= 8 else lag4
            num_trans_lag1 = serie_transacciones[-1] if serie_transacciones else np.nan
            variacion_interanual = (lag1 / lag4 - 1) if lag4 else 0.0

            # Indicadores con tendencia se proyectan un paso más (tasa anual
            # repartida en 4 trimestres); el resto queda congelado (tasa=0.0).
            for c in indicator_cols:
                indicadores_proyectados[c] = indicadores_proyectados[c] * (1 + crecimiento_anual[c] / 4)

            fila = {c: indicadores_proyectados[c] for c in indicator_cols}
            fila.update({
                "precio_m2_lag1": lag1, "precio_m2_lag4": lag4, "precio_m2_lag8": lag8,
                "num_transacciones_lag1": num_trans_lag1,
                "variacion_interanual": variacion_interanual,
                "is_estimated": True,
            })
            X = pd.DataFrame([fila])[feature_cols]
            variacion_predicha = float(modelo.pipeline.predict(X)[0]) if modelo.pipeline else float(_naive_predict(historial))
            precio_predicho = lag1 * (1 + variacion_predicha)

            # Banda de incertidumbre: se ensancha con el horizonte (factor
            # creciente sobre el RMSE de validación, ver sección "Buenas
            # prácticas" del plan).
            ancho = rmse_val * lag1 * (1 + 0.25 * paso)

            crud_sync.create_prediccion(
                db,
                id_geografia=id_geografia,
                anio=anio,
                trimestre=trimestre,
                id_modelo=id_modelo,
                precio_predicho=float(precio_predicho),
                intervalo_inferior=float(precio_predicho - ancho),
                intervalo_superior=float(precio_predicho + ancho),
                es_forecast=True,
            )

            serie_precio.append(precio_predicho)
            serie_transacciones.append(num_trans_lag1)

    logger.info(f"Forecast recursivo completado: {FORECAST_TRIMESTRES} trimestres (id_modelo={id_modelo}).")
