
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select anio
from "postgres"."core"."dim_tiempo"
where anio is null



  
  
      
    ) dbt_internal_test