{{ config(materialized='view') }}

-- Nota: el Índice de Gini se mantiene en su escala nativa del INE (0-100),
-- NO se normaliza a 0-1. Ver especificacion_carga_datos_TFM.md.
SELECT
    37706 AS codigo_ine_fuente,
    CASE WHEN "Distritos" IS NOT NULL THEN LEFT("Distritos", 7) ELSE LEFT("Municipios", 5) END AS geografia_codigo_ine,
    CASE WHEN "Distritos" IS NOT NULL THEN 'DISTRITO' ELSE 'MUNICIPIO' END AS nivel_geografico,
    "Indice de Gini y Distribucion de la renta P80/P20" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(REPLACE(REPLACE(TRIM("Total"), '.', ''), ',', '.') AS NUMERIC(18, 4)) AS valor
FROM {{ source('staging', 'ine_gini_p80p20') }}
WHERE TRIM("Municipios") = '29067 Málaga'
  AND ("Secciones" IS NULL OR TRIM("Secciones") = '')
