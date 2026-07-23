
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    nombre_tipo as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_tipo_vivienda"
where nombre_tipo is not null
group by nombre_tipo
having count(*) > 1



  
  
      
    ) dbt_internal_test