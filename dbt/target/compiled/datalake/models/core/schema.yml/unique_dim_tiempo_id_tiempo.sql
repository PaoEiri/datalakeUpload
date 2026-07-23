
    
    

select
    id_tiempo as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_tiempo"
where id_tiempo is not null
group by id_tiempo
having count(*) > 1


