
    
    

with all_values as (

    select
        nombre_indicador as value_field,
        count(*) as n_records

    from "postgres"."staging"."stg_poblacion_sexo"
    group by nombre_indicador

)

select *
from all_values
where value_field not in (
    'Total','Hombres','Mujeres'
)


