
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select anio
from "postgres"."intermediate"."int_indicadores_unificado"
where anio is null



  
  
      
    ) dbt_internal_test