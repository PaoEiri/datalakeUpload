
  
    

  create  table "postgres"."marts"."fact_indicadores_anuales__dbt_tmp"
  
  
    
  
  (
    id_tiempo bigint not null references "postgres"."core"."dim_tiempo" (id_tiempo),
    id_geografia integer not null references "postgres"."core"."dim_geografia" (id_geografia),
    id_indicador integer not null references "postgres"."core"."dim_indicador" (id_indicador),
    valor numeric(18,4),
    
    unique (id_tiempo, id_geografia, id_indicador)
    )
 ;
    insert into "postgres"."marts"."fact_indicadores_anuales__dbt_tmp" (
      id_tiempo, id_geografia, id_indicador, valor
    )
  
  (
    
    select id_tiempo, id_geografia, id_indicador, valor
    from (
        

-- Grano: tiempo (anual) x geografía x indicador -> valor
-- id_indicador ya viene canónico (colapsado) desde intermediate.
-- Solo FKs + métrica: ver nota de esquema en fact_precio_vivienda.sql.
SELECT
    dt.id_tiempo,
    dg.id_geografia,
    ii.id_indicador,
    ii.valor
FROM "postgres"."intermediate"."int_indicadores_unificado" ii
LEFT JOIN "postgres"."core"."dim_tiempo"     dt ON ii.anio = dt.anio AND dt.trimestre IS NULL
LEFT JOIN "postgres"."core"."dim_geografia"  dg ON ii.geografia_codigo_ine = dg.codigo_ine AND UPPER(dg.nivel) = ii.nivel_geografico
    ) as model_subq
  );
  