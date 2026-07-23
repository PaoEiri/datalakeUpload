
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_tipo_vivienda
from "postgres"."core"."dim_tipo_vivienda"
where id_tipo_vivienda is null



  
  
      
    ) dbt_internal_test