
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_tiempo as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_tiempo"
where id_tiempo is not null
group by id_tiempo
having count(*) > 1



  
  
      
    ) dbt_internal_test