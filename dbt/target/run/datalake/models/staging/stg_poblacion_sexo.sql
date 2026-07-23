
  create view "postgres"."staging"."stg_poblacion_sexo__dbt_tmp"
    
    
  as (
    

SELECT
    2882 AS codigo_ine_fuente,
    LEFT("Municipios", 5) AS geografia_codigo_ine,
    'MUNICIPIO' AS nivel_geografico,
    "Sexo" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(REPLACE(REPLACE(TRIM("Total"), '.', ''), ',', '.') AS NUMERIC(18, 4)) AS valor
FROM "postgres"."staging"."ine_poblacion_sexo"
WHERE TRIM("Municipios") = '29067 Málaga'
  );