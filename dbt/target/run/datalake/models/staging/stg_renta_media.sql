
  create view "postgres"."staging"."stg_renta_media__dbt_tmp"
    
    
  as (
    

SELECT
    COALESCE("Distritos", "Municipios") AS geografia_nombre,
    CASE
        WHEN "Distritos" IS NOT NULL THEN 'DISTRITO'
        ELSE 'MUNICIPIO'
    END AS nivel_geografico,
    indicador_renta AS nombre_indicador,
    CAST("Periodo" AS INTEGER) AS anio,
    CAST(REPLACE("Total", ',', '.') AS NUMERIC) AS valor
FROM "postgres"."staging"."renta_media"
WHERE "Secciones" IS NULL
  );