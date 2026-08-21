
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_modelo as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_modelo"
where id_modelo is not null
group by id_modelo
having count(*) > 1



  
  
      
    ) dbt_internal_test