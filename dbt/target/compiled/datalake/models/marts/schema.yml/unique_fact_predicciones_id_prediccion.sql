
    
    

select
    id_prediccion as unique_field,
    count(*) as n_records

from "postgres"."marts"."fact_predicciones"
where id_prediccion is not null
group by id_prediccion
having count(*) > 1


