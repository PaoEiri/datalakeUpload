
  create view "postgres"."staging"."stg_indicadores_ine__dbt_tmp"
    
    
  as (
    

SELECT * FROM "postgres"."staging"."stg_indicadores_malaga"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_indicadores_malaga_distrito"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_indicadores_turismo"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_gini_p20_distritos"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_poblacion_sexo"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_fuentes_ingreso"
UNION ALL
SELECT * FROM "postgres"."staging"."stg_renta_media"
  );