

SELECT
    69330 AS codigo_ine_fuente,
    '29067' AS geografia_codigo_ine,
    'MUNICIPIO' AS nivel_geografico,
    "Indicadores" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(NULLIF(REPLACE(REPLACE(TRIM("Total"), '.', ''), ',', '.'), '') AS NUMERIC(18, 4)) AS valor
FROM "postgres"."staging"."ine_hogares_vivienda_seguridad"
WHERE TRIM("Municipios") = 'Málaga'