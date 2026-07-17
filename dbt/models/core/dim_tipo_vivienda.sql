{{ config(materialized='table') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY tipo_vivienda) AS id_tipo_vivienda,
    tipo_vivienda                               AS nombre_tipo,
    CASE tipo_vivienda
        WHEN 'General'               THEN 'Todos los tipos'
        WHEN 'Vivienda nueva'        THEN 'Primera transmision'
        WHEN 'Vivienda segunda mano' THEN 'Segunda transmision'
        ELSE tipo_vivienda
    END AS descripcion
FROM (
    SELECT DISTINCT tipo_vivienda
    FROM {{ source('staging', 'ipv_precios_vivienda') }}
    WHERE tipo_vivienda IS NOT NULL
) t