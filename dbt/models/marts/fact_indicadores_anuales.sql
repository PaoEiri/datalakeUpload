{{ config(materialized='table') }}

-- Grano: tiempo (anual) x geografía x indicador -> valor
-- id_indicador ya viene canónico (colapsado) desde intermediate.
-- Solo FKs + métrica: ver nota de esquema en fact_precio_vivienda.sql.
SELECT
    dt.id_tiempo,
    dg.id_geografia,
    ii.id_indicador,
    ii.valor
FROM {{ ref('int_indicadores_unificado') }} ii
LEFT JOIN {{ ref('dim_tiempo') }}     dt ON ii.anio = dt.anio AND dt.trimestre IS NULL
LEFT JOIN {{ ref('dim_geografia') }}  dg ON ii.geografia_codigo_ine = dg.codigo_ine AND UPPER(dg.nivel) = ii.nivel_geografico
