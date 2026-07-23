
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        nombre_tipo as value_field,
        count(*) as n_records

    from "postgres"."core"."dim_tipo_vivienda"
    group by nombre_tipo

)

select *
from all_values
where value_field not in (
    'libre','segunda mano','nueva','protegida'
)



  
  
      
    ) dbt_internal_test