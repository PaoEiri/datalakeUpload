
  create view "postgres"."staging"."stg_ipv__dbt_tmp"
    
    
  as (
    

SELECT
    tipo_vivienda,
    ambito,
    comunidad,
    indicador,
    anio,
    trimestre,
    fecha,
    valor,
    fuente,
    cargado_en
FROM "postgres"."staging"."ipv_precios_vivienda"
WHERE fecha IS NOT NULL
  );