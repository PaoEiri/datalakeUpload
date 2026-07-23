
  create view "postgres"."staging"."stg_transacciones_segunda_mano__dbt_tmp"
    
    
  as (
    

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'segunda mano' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_segunda_mano"
  );