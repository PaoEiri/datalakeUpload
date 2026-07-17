
  
    

  create  table "postgres"."marts"."fct_precios_vivienda__dbt_tmp"
  
  
    as
  
  (
    

SELECT
    -- claves surrogadas de dimensiones
    dc.id_comunidad,
    dt.id_tiempo,
    di.id_indicador,
    dtv.id_tipo_vivienda,

    -- atributos de contexto útiles en Power BI
    stg.ambito,
    dt.fecha,
    dt.anio,
    dt.trimestre,
    dt.label_periodo,
    dc.nombre_comunidad,
    dc.codigo_ine,
    di.nombre_indicador,
    di.tipo_indicador,
    dtv.nombre_tipo,

    -- métrica
    stg.valor,

    -- trazabilidad
    stg.fuente,
    stg.cargado_en

FROM "postgres"."staging"."stg_ipv" stg

LEFT JOIN "postgres"."core"."dim_comunidad"     dc  ON stg.comunidad  = dc.nombre_comunidad
LEFT JOIN "postgres"."core"."dim_tiempo"        dt  ON stg.fecha       = dt.fecha
LEFT JOIN "postgres"."core"."dim_indicador"     di  ON stg.indicador   = di.nombre_indicador
LEFT JOIN "postgres"."core"."dim_tipo_vivienda" dtv ON stg.tipo_vivienda = dtv.nombre_tipo
  );
  