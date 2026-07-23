{{ config(materialized='table') }}

-- Grano: tiempo (trimestral) x geografía -> precio_m2
SELECT
    dt.id_tiempo,
    ip.id_geografia,
    dt.anio,
    dt.trimestre,
    dt.fecha,
    dg.nombre AS geografia_nombre,
    dg.nivel AS geografia_nivel,
    ip.precio_m2
FROM {{ ref('int_precios_vivienda_unificado') }} ip
LEFT JOIN {{ ref('dim_tiempo') }}    dt ON ip.anio = dt.anio AND ip.trimestre = dt.trimestre
LEFT JOIN {{ ref('dim_geografia') }} dg ON ip.id_geografia = dg.id_geografia
