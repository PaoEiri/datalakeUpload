
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select num_transacciones
from "postgres"."staging"."stg_transacciones_libre"
where num_transacciones is null



  
  
      
    ) dbt_internal_test