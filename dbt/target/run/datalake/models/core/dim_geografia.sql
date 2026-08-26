
  
    

  create  table "postgres"."core"."dim_geografia__dbt_tmp"
  
  
    
  
  (
    id_geografia integer not null,
    nombre text not null,
    codigo_ine character varying(10),
    es_codigo_oficial_ine boolean,
    nivel text not null,
    nivel_orden integer,
    codigo_municipio integer,
    codigo_provincia integer,
    codigo_ccaa integer,
    codigo_pais integer,
    
    primary key (id_geografia)
    )
 ;
    insert into "postgres"."core"."dim_geografia__dbt_tmp" (
      id_geografia, nombre, codigo_ine, es_codigo_oficial_ine, nivel, nivel_orden, codigo_municipio, codigo_provincia, codigo_ccaa, codigo_pais
    )
  
  (
    
    select id_geografia, nombre, codigo_ine, es_codigo_oficial_ine, nivel, nivel_orden, codigo_municipio, codigo_provincia, codigo_ccaa, codigo_pais
    from (
        

-- Pass-through del seed: dim_geografia ya viene cerrada y verificada
-- (15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía,
-- España). Ver especificacion_carga_datos_TFM.md.
SELECT
    id_geografia,
    nombre,
    codigo_ine,
    es_codigo_oficial_ine,
    nivel,
    nivel_orden,
    codigo_municipio,
    codigo_provincia,
    codigo_ccaa,
    codigo_pais
FROM "postgres"."reference"."dim_geografia"
    ) as model_subq
  );
  