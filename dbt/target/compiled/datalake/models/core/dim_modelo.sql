

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
    -- Holdout final (2025T1-2026T2), nunca visto durante desarrollo — el
    -- desempeño real esperado del modelo (ver consideraciones/pipeline_machine_learning.md).
    -- r2/rmse/mae/accuracy_direccional de arriba son de desarrollo (walk-forward).
    r2_holdout,
    rmse_holdout,
    mae_holdout,
    accuracy_direccional_holdout,
    indicadores_usados,
    importancia_features
FROM "postgres"."public"."ml_model_registry"