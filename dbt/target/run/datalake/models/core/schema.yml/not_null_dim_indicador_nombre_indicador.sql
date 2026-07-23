
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nombre_indicador
from "postgres"."core"."dim_indicador"
where nombre_indicador is null



  
  
      
    ) dbt_internal_test