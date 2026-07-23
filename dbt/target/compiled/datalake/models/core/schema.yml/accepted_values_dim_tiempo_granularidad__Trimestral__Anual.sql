
    
    

with all_values as (

    select
        granularidad as value_field,
        count(*) as n_records

    from "postgres"."core"."dim_tiempo"
    group by granularidad

)

select *
from all_values
where value_field not in (
    'Trimestral','Anual'
)


