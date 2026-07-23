
    
    

select
    nombre_tipo as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_tipo_vivienda"
where nombre_tipo is not null
group by nombre_tipo
having count(*) > 1


