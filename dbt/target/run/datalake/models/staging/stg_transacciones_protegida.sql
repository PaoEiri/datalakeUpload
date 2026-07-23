
  create view "postgres"."staging"."stg_transacciones_protegida__dbt_tmp"
    
    
  as (
    

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'protegida' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_protegida"
  );