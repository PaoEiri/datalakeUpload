
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_indicador as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_indicador"
where id_indicador is not null
group by id_indicador
having count(*) > 1



  
  
      
    ) dbt_internal_test