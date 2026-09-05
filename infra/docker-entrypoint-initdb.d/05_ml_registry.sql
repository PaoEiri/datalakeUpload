-- Pipeline de ML: predicción de variación trimestral de precio_m2 (municipal).
-- Ver consideraciones/instrucciones_ml_claude_code.md para el diseño completo.

ALTER TABLE reference.seed_indicadores_fuentes
    ADD COLUMN IF NOT EXISTS usar_en_ml BOOLEAN NOT NULL DEFAULT FALSE;

-- Punto de partida (sección 2 de las instrucciones) — ajustable después desde
-- la pestaña "Indicadores" de la UI (columna "Usar en ML"), no es una lista fija.
UPDATE reference.seed_indicadores_fuentes
SET usar_en_ml = TRUE
WHERE indicador_id IN (27, 47, 73, 24, 23, 40, 75, 42, 33, 35, 77, 21, 26, 30);

CREATE TABLE IF NOT EXISTS public.mart_features_ml (
    id_geografia            INT NOT NULL,
    id_tiempo               INT NOT NULL,
    anio                    INT NOT NULL,
    trimestre               INT NOT NULL,
    precio_m2               NUMERIC(18, 4),
    num_transacciones       INT,
    precio_m2_lag1          NUMERIC(18, 4),
    precio_m2_lag4          NUMERIC(18, 4),
    precio_m2_lag8          NUMERIC(18, 4),
    num_transacciones_lag1  INT,
    variacion_interanual    NUMERIC(18, 6),
    is_estimated            BOOLEAN NOT NULL DEFAULT FALSE,
    target                  NUMERIC(18, 6),
    -- columnas de indicadores: se agregan dinámicamente (ALTER TABLE ... ADD
    -- COLUMN IF NOT EXISTS) desde build_features() según usar_en_ml=true,
    -- no se enumeran aquí porque la lista es configurable.
    PRIMARY KEY (id_geografia, id_tiempo)
);

CREATE TABLE IF NOT EXISTS public.ml_model_registry (
    id_modelo              SERIAL PRIMARY KEY,
    version                VARCHAR(50) NOT NULL UNIQUE,
    algoritmo               VARCHAR(20) NOT NULL
        CHECK (algoritmo IN ('naive', 'ridge', 'xgboost', 'sarimax')),
    fecha_entrenamiento     TIMESTAMP NOT NULL DEFAULT now(),
    hiperparametros         JSON,
    indicadores_usados      JSON,
    importancia_features    JSON,
    r2                      NUMERIC(10, 6),
    accuracy_direccional    NUMERIC(10, 6),
    rmse                    NUMERIC(18, 6),
    mae                     NUMERIC(18, 6),
    -- Holdout final (2025T1-2026T2), nunca visto durante desarrollo — ver
    -- src/tasks/ml.py::_evaluar_holdout. Desempeño real esperado.
    r2_holdout                      NUMERIC(10, 6),
    accuracy_direccional_holdout    NUMERIC(10, 6),
    rmse_holdout                    NUMERIC(18, 6),
    mae_holdout                     NUMERIC(18, 6),
    es_champion             BOOLEAN NOT NULL DEFAULT FALSE,
    ruta_minio_modelo       VARCHAR(300),
    ruta_minio_shap         VARCHAR(300)
);

-- Tabla operativa (no dbt): la escribe el flow de Python
-- (flows/05_ml_train.py vía src/db/crud_sync.py::create_prediccion). dbt la
-- lee como source (dbt/models/marts/sources.yml) y la transforma en
-- marts.fact_predicciones (dbt/models/marts/fact_predicciones.sql),
-- resolviendo id_tiempo por join a dim_tiempo — dim_tiempo ahora genera
-- trimestres futuros (ver dbt/models/core/dim_tiempo.sql), así que no hace
-- falta guardar id_tiempo aquí, solo anio/trimestre.
CREATE TABLE IF NOT EXISTS public.predicciones_ml_raw (
    id_prediccion           SERIAL PRIMARY KEY,
    id_geografia            INT NOT NULL,
    anio                    INT NOT NULL,
    trimestre               INT NOT NULL,
    id_modelo               INT NOT NULL REFERENCES public.ml_model_registry(id_modelo),
    precio_predicho         NUMERIC(18, 4) NOT NULL,
    intervalo_inferior      NUMERIC(18, 4),
    intervalo_superior      NUMERIC(18, 4),
    es_forecast             BOOLEAN NOT NULL,
    creado_en               TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (id_geografia, anio, trimestre, id_modelo)
);
