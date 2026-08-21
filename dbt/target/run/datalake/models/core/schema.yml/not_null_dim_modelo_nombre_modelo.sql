
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nombre_modelo
from "postgres"."core"."dim_modelo"
where nombre_modelo is null



  
  
      
    ) dbt_internal_test