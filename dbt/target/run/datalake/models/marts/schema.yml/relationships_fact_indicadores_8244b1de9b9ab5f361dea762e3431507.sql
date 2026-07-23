
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select id_indicador as from_field
    from "postgres"."marts"."fact_indicadores_anuales"
    where id_indicador is not null
),

parent as (
    select id_indicador as to_field
    from "postgres"."core"."dim_indicador"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test