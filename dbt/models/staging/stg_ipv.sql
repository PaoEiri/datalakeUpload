{{ config(materialized='view') }}

SELECT
    tipo_vivienda,
    ambito,
    comunidad,
    indicador,
    anio,
    trimestre,
    fecha,
    valor,
    fuente,
    cargado_en
FROM {{ source('staging', 'ipv_precios_vivienda') }}
WHERE fecha IS NOT NULL