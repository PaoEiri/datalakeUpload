{{ config(materialized='view') }}

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'segunda mano' AS tipo_vivienda
FROM {{ source('staging', 'transacciones_segunda_mano') }}
