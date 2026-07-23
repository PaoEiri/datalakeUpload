{{ config(materialized='view') }}

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'nueva' AS tipo_vivienda
FROM {{ source('staging', 'transacciones_nueva') }}
