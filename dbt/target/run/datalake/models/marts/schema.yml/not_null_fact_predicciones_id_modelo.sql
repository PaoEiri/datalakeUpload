
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_modelo
from "postgres"."marts"."fact_predicciones"
where id_modelo is null



  
  
      
    ) dbt_internal_test