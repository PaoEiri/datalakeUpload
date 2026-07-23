
    
    

select
    id_tipo_vivienda as unique_field,
    count(*) as n_records

from "postgres"."core"."dim_tipo_vivienda"
where id_tipo_vivienda is not null
group by id_tipo_vivienda
having count(*) > 1


