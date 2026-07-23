
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        nivel_geografico as value_field,
        count(*) as n_records

    from "postgres"."staging"."stg_indicadores_fuente_ingreso"
    group by nivel_geografico

)

select *
from all_values
where value_field not in (
    'MUNICIPIO','DISTRITO'
)



  
  
      
    ) dbt_internal_test