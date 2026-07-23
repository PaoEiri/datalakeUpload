
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select precio_m2
from "postgres"."staging"."stg_precios_tinsa"
where precio_m2 is null



  
  
      
    ) dbt_internal_test