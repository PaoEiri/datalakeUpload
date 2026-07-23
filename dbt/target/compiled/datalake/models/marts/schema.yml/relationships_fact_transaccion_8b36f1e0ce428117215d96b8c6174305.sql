
    
    

with child as (
    select id_tiempo as from_field
    from "postgres"."marts"."fact_transacciones_inmobiliarias"
    where id_tiempo is not null
),

parent as (
    select id_tiempo as to_field
    from "postgres"."core"."dim_tiempo"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


