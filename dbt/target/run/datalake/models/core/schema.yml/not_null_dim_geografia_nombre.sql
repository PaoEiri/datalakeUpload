
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nombre
from "postgres"."core"."dim_geografia"
where nombre is null



  
  
      
    ) dbt_internal_test