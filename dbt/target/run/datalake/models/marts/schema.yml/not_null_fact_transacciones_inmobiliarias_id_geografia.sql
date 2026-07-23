
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_geografia
from "postgres"."marts"."fact_transacciones_inmobiliarias"
where id_geografia is null



  
  
      
    ) dbt_internal_test