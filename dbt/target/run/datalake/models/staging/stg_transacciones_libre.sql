
  create view "postgres"."staging"."stg_transacciones_libre__dbt_tmp"
    
    
  as (
    

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'libre' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_libre"
  );