
  
    

  create  table "postgres"."core"."dim_modelo__dbt_tmp"
  
  
    
  
  (
    id_modelo integer not null,
    nombre_modelo character varying(20) not null,
    version character varying(50),
    fecha_entrenamiento timestamp without time zone,
    es_champion boolean,
    r2 numeric(10,6),
    rmse numeric(18,6),
    mae numeric(18,6),
    accuracy_direccional numeric(10,6),
    indicadores_usados json,
    importancia_features json,
    
    primary key (id_modelo)
    )
 ;
    insert into "postgres"."core"."dim_modelo__dbt_tmp" (
      id_modelo, nombre_modelo, version, fecha_entrenamiento, es_champion, r2, rmse, mae, accuracy_direccional, indicadores_usados, importancia_features
    )
  
  (
    
    select id_modelo, nombre_modelo, version, fecha_entrenamiento, es_champion, r2, rmse, mae, accuracy_direccional, indicadores_usados, importancia_features
    from (
        

-- La escribe el flow de ML (flows/05_ml_train.py) en la tabla operativa
-- public.ml_model_registry (source, no dbt). r2/rmse/mae/accuracy_direccional
-- son las métricas reales calculadas en walk-forward validation
-- (src/tasks/ml.py) — se exponen las 4, no una sola "metrica_error"
-- genérica, para poder explorarlas en Power BI.
SELECT
    id_modelo,
    algoritmo AS nombre_modelo,
    version,
    fecha_entrenamiento,
    es_champion,
    r2,
    rmse,
    mae,
    accuracy_direccional,
    indicadores_usados,
    importancia_features
FROM "postgres"."public"."ml_model_registry"
    ) as model_subq
  );
  