
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select anio
from "postgres"."staging"."stg_indicadores_demograficos_municipio"
where anio is null



  
  
      
    ) dbt_internal_test