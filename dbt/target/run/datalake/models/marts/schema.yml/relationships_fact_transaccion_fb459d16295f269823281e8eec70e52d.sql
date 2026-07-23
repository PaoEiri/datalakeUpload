
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select id_tipo_vivienda as from_field
    from "postgres"."marts"."fact_transacciones_inmobiliarias"
    where id_tipo_vivienda is not null
),

parent as (
    select id_tipo_vivienda as to_field
    from "postgres"."core"."dim_tipo_vivienda"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test