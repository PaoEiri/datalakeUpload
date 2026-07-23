
    
    

with all_values as (

    select
        nivel_geografico as value_field,
        count(*) as n_records

    from "postgres"."staging"."stg_indicadores_renta_persona_hogar"
    group by nivel_geografico

)

select *
from all_values
where value_field not in (
    'MUNICIPIO','DISTRITO'
)


