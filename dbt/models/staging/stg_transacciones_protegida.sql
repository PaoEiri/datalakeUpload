{{ config(materialized='view') }}

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'protegida' AS tipo_vivienda
FROM {{ source('staging', 'transacciones_protegida') }}
