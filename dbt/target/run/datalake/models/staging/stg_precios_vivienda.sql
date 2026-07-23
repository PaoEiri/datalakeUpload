
  create view "postgres"."staging"."stg_precios_vivienda__dbt_tmp"
    
    
  as (
    

SELECT
    zona            AS geografia_nombre,
    nivel_geografico,
    anio,
    trimestre,
    fecha,
    valor           AS precio_m2,
    fuente,
    cargado_en
FROM "postgres"."staging"."tinsa_precios_vivienda"
WHERE fecha IS NOT NULL
  );