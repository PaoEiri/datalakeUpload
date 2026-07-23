{{ config(materialized='view') }}

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'libre' AS tipo_vivienda
FROM {{ source('staging', 'transacciones_libre') }}
