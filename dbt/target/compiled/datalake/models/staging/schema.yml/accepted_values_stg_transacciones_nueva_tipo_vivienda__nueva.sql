
    
    

with all_values as (

    select
        tipo_vivienda as value_field,
        count(*) as n_records

    from "postgres"."staging"."stg_transacciones_nueva"
    group by tipo_vivienda

)

select *
from all_values
where value_field not in (
    'nueva'
)


