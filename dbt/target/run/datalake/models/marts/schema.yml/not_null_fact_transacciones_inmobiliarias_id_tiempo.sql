
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_tiempo
from "postgres"."marts"."fact_transacciones_inmobiliarias"
where id_tiempo is null



  
  
      
    ) dbt_internal_test