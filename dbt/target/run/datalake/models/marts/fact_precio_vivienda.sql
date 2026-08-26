
  
    

  create  table "postgres"."marts"."fact_precio_vivienda__dbt_tmp"
  
  
    
  
  (
    id_tiempo bigint not null references "postgres"."core"."dim_tiempo" (id_tiempo),
    id_geografia integer not null references "postgres"."core"."dim_geografia" (id_geografia),
    precio_m2 numeric(18,4),
    
    unique (id_tiempo, id_geografia)
    )
 ;
    insert into "postgres"."marts"."fact_precio_vivienda__dbt_tmp" (
      id_tiempo, id_geografia, precio_m2
    )
  
  (
    
    select id_tiempo, id_geografia, precio_m2
    from (
        

-- Grano: tiempo (trimestral) x geografía -> precio_m2
-- Solo FKs + métrica: los atributos descriptivos (anio, trimestre, fecha,
-- nombre/nivel de geografía) viven en dim_tiempo/dim_geografia, accesibles
-- vía id_tiempo/id_geografia — repetirlos aquí rompería el filtrado cruzado
-- en Power BI (un slicer de dim_geografia[nombre] no filtraría esta tabla).
SELECT
    dt.id_tiempo,
    ip.id_geografia,
    ip.precio_m2
FROM "postgres"."intermediate"."int_precios_vivienda_unificado" ip
LEFT JOIN "postgres"."core"."dim_tiempo" dt ON ip.anio = dt.anio AND ip.trimestre = dt.trimestre
    ) as model_subq
  );
  