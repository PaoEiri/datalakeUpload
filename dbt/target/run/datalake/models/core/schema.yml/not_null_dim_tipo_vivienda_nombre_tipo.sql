
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nombre_tipo
from "postgres"."core"."dim_tipo_vivienda"
where nombre_tipo is null



  
  
      
    ) dbt_internal_test