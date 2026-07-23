
    
    

with all_values as (

    select
        tipo_vivienda as value_field,
        count(*) as n_records

    from "postgres"."intermediate"."int_transacciones_unificado"
    group by tipo_vivienda

)

select *
from all_values
where value_field not in (
    'libre','segunda mano','nueva','protegida'
)


