
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select slug_tinsa
from "postgres"."staging"."stg_precios_tinsa"
where slug_tinsa is null



  
  
      
    ) dbt_internal_test