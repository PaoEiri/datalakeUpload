
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select trimestre
from "postgres"."intermediate"."int_precios_vivienda_unificado"
where trimestre is null



  
  
      
    ) dbt_internal_test