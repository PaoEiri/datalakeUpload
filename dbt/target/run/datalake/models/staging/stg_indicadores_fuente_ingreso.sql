
  create view "postgres"."staging"."stg_indicadores_fuente_ingreso__dbt_tmp"
    
    
  as (
    

SELECT
    31107 AS codigo_ine_fuente,
    CASE WHEN "Distritos" IS NOT NULL THEN LEFT("Distritos", 7) ELSE LEFT("Municipios", 5) END AS geografia_codigo_ine,
    CASE WHEN "Distritos" IS NOT NULL THEN 'DISTRITO' ELSE 'MUNICIPIO' END AS nivel_geografico,
    "Distribucion por fuente de ingresos" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(REPLACE(REPLACE(TRIM(valor_porcentaje), '.', ''), ',', '.') AS NUMERIC(18, 4)) AS valor
FROM "postgres"."staging"."ine_fuente_ingreso"
WHERE TRIM("Municipios") = '29067 Málaga'
  AND ("Secciones" IS NULL OR TRIM("Secciones") = '')
  );