
  create view "postgres"."staging"."stg_indicadores_malaga_distrito__dbt_tmp"
    
    
  as (
    

SELECT
    COALESCE("Distritos", "Municipios") AS geografia_nombre,
    CASE
        WHEN "Distritos" IS NOT NULL THEN 'DISTRITO'
        ELSE 'MUNICIPIO'
    END AS nivel_geografico,
    indice_demografico AS nombre_indicador,
    CAST("Periodo" AS INTEGER) AS anio,
    CAST(REPLACE("Total", ',', '.') AS NUMERIC) AS valor
FROM "postgres"."staging"."indicadores_malaga_distrito"
WHERE "Secciones" IS NULL
  );