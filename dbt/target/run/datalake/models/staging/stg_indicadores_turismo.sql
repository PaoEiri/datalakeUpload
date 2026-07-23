
  create view "postgres"."staging"."stg_indicadores_turismo__dbt_tmp"
    
    
  as (
    

SELECT
    69307 AS codigo_ine_fuente,
    '29067' AS geografia_codigo_ine,
    'MUNICIPIO' AS nivel_geografico,
    "Indicadores" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(REPLACE(REPLACE(TRIM("Total"), '.', ''), ',', '.') AS NUMERIC(18, 4)) AS valor
FROM "postgres"."staging"."ine_turismo"
WHERE TRIM("Municipios") = 'Málaga'
  );