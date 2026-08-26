
  
    

  create  table "postgres"."marts"."fact_predicciones__dbt_tmp"
  
  
    
  
  (
    id_tiempo bigint not null references "postgres"."core"."dim_tiempo" (id_tiempo),
    id_geografia integer not null references "postgres"."core"."dim_geografia" (id_geografia),
    id_modelo integer not null references "postgres"."core"."dim_modelo" (id_modelo),
    id_prediccion integer not null,
    precio_predicho numeric(18,4),
    intervalo_inferior numeric(18,4),
    intervalo_superior numeric(18,4),
    es_forecast boolean,
    creado_en timestamp without time zone,
    
    primary key (id_prediccion)
    )
 ;
    insert into "postgres"."marts"."fact_predicciones__dbt_tmp" (
      id_tiempo, id_geografia, id_modelo, id_prediccion, precio_predicho, intervalo_inferior, intervalo_superior, es_forecast, creado_en
    )
  
  (
    
    select id_tiempo, id_geografia, id_modelo, id_prediccion, precio_predicho, intervalo_inferior, intervalo_superior, es_forecast, creado_en
    from (
        

-- Grano: tiempo (trimestral) x geografía x modelo -> precio_predicho
-- La escribe el flow de ML (flows/05_ml_train.py) en la tabla operativa
-- public.predicciones_ml_raw (source, no dbt) — este modelo solo resuelve
-- id_tiempo por join, igual que el resto de las fact tables (ver nota de
-- esquema en fact_precio_vivienda.sql). id_prediccion/es_forecast quedan
-- como dimensiones degeneradas propias del hecho.
SELECT
    dt.id_tiempo,
    p.id_geografia,
    p.id_modelo,
    p.id_prediccion,
    p.precio_predicho,
    p.intervalo_inferior,
    p.intervalo_superior,
    p.es_forecast,
    p.creado_en
FROM "postgres"."public"."predicciones_ml_raw" p
LEFT JOIN "postgres"."core"."dim_tiempo" dt ON p.anio = dt.anio AND p.trimestre = dt.trimestre
    ) as model_subq
  );
  