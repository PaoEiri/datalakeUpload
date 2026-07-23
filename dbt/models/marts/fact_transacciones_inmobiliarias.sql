{{ config(materialized='table') }}

-- Grano: tiempo (trimestral) x geografía (municipio) x tipo_vivienda -> num_transacciones
-- Hoy solo id_geografia del municipio de Málaga (ver int_transacciones_unificado.sql).
SELECT
    dt.id_tiempo,
    it.id_geografia,
    dtv.id_tipo_vivienda,
    dt.anio,
    dt.trimestre,
    dt.fecha,
    dg.nombre AS geografia_nombre,
    dtv.nombre_tipo,
    it.num_transacciones
FROM {{ ref('int_transacciones_unificado') }} it
LEFT JOIN {{ ref('dim_tiempo') }}        dt  ON it.anio = dt.anio AND it.trimestre = dt.trimestre
LEFT JOIN {{ ref('dim_geografia') }}     dg  ON it.id_geografia = dg.id_geografia
LEFT JOIN {{ ref('dim_tipo_vivienda') }} dtv ON it.tipo_vivienda = dtv.nombre_tipo
