
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select valor
from "postgres"."intermediate"."int_indicadores_unificado"
where valor is null



  
  
      
    ) dbt_internal_test