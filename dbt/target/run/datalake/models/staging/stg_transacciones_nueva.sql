
  create view "postgres"."staging"."stg_transacciones_nueva__dbt_tmp"
    
    
  as (
    

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'nueva' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_nueva"
  );