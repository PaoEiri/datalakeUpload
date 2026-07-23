
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_geografia as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_geografia"
where id_geografia is not null
group by id_geografia
having count(*) > 1



  
  
      
    ) dbt_internal_test