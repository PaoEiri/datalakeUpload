

-- Grano: tiempo (trimestral) x geografía x modelo -> precio_predicho
-- La escribe el flow de ML (flows/05_ml_train.py) en la tabla operativa
-- public.predicciones_ml_raw (source, no dbt) — este modelo solo resuelve
-- id_tiempo por join, igual que el resto de las fact tables (ver nota de
-- esquema en fact_precio_vivienda.sql). id_prediccion/es_forecast quedan
-- como dimensiones degeneradas propias del hecho.
SELECT
    dt.id_tiempo,
    p.id_geografia,
    p.id_modelo,
    p.id_prediccion,
    p.precio_predicho,
    p.intervalo_inferior,
    p.intervalo_superior,
    p.es_forecast,
    p.creado_en
FROM "postgres"."public"."predicciones_ml_raw" p
LEFT JOIN "postgres"."core"."dim_tiempo" dt ON p.anio = dt.anio AND p.trimestre = dt.trimestre