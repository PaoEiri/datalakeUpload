
    
    

with child as (
    select id_modelo as from_field
    from "postgres"."marts"."fact_predicciones"
    where id_modelo is not null
),

parent as (
    select id_modelo as to_field
    from "postgres"."core"."dim_modelo"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


