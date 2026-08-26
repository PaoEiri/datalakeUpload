
  
    

  create  table "postgres"."core"."dim_tipo_vivienda__dbt_tmp"
  
  
    
  
  (
    id_tipo_vivienda integer not null,
    nombre_tipo text not null,
    
    primary key (id_tipo_vivienda)
    )
 ;
    insert into "postgres"."core"."dim_tipo_vivienda__dbt_tmp" (
      id_tipo_vivienda, nombre_tipo
    )
  
  (
    
    select id_tipo_vivienda, nombre_tipo
    from (
        

-- Solo 4 tipos atómicos; NO incluye "total" (antipatrón de doble conteo,
-- ver especificacion_carga_datos_TFM.md regla transversal nº4).
SELECT *
FROM (
    VALUES
        (1, 'libre'),
        (2, 'segunda mano'),
        (3, 'nueva'),
        (4, 'protegida')
) AS t(id_tipo_vivienda, nombre_tipo)
    ) as model_subq
  );
  