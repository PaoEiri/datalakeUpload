
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        tipo_vivienda as value_field,
        count(*) as n_records

    from "postgres"."staging"."stg_transacciones_protegida"
    group by tipo_vivienda

)

select *
from all_values
where value_field not in (
    'protegida'
)



  
  
      
    ) dbt_internal_test