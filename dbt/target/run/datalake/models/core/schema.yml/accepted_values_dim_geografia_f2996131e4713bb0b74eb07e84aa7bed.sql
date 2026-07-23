
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        nivel as value_field,
        count(*) as n_records

    from "postgres"."core"."dim_geografia"
    group by nivel

)

select *
from all_values
where value_field not in (
    'Distrito','Municipio','Provincia','Comunidad Autónoma','País'
)



  
  
      
    ) dbt_internal_test