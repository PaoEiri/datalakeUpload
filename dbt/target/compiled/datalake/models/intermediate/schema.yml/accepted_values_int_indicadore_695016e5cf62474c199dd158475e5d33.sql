
    
    

with all_values as (

    select
        nivel_geografico as value_field,
        count(*) as n_records

    from "postgres"."intermediate"."int_indicadores_unificado"
    group by nivel_geografico

)

select *
from all_values
where value_field not in (
    'MUNICIPIO','DISTRITO'
)


