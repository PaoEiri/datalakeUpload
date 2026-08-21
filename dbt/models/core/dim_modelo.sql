{{ config(materialized='table') }}

-- La escribe el flow de ML (flows/05_ml_train.py) en la tabla operativa
-- public.ml_model_registry (source, no dbt). r2/rmse/mae/accuracy_direccional
-- son las métricas reales calculadas en walk-forward validation
-- (src/tasks/ml.py) — se exponen las 4, no una sola "metrica_error"
-- genérica, para poder explorarlas en Power BI.
SELECT
    id_modelo,
    algoritmo AS nombre_modelo,
    version,
    fecha_entrenamiento,
    es_champion,
    r2,
    rmse,
    mae,
    accuracy_direccional,
    indicadores_usados,
    importancia_features
FROM {{ source('ml_registry', 'ml_model_registry') }}
