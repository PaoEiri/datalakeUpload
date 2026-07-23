
    
    

with child as (
    select id_geografia as from_field
    from "postgres"."marts"."fact_precios_vivienda"
    where id_geografia is not null
),

parent as (
    select id_geografia as to_field
    from "postgres"."core"."dim_geografia"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


