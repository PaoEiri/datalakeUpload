

SELECT
    -- claves surrogadas de dimensiones
    dt.id_tiempo,
    dg.id_geografia,

    -- atributos de contexto útiles en Power BI
    dt.fecha,
    dt.anio,
    dt.trimestre,
    dt.label_periodo,
    dg.geografia_nombre,
    dg.nivel_geografico,

    -- métrica
    stg.precio_m2,

    -- trazabilidad
    stg.fuente,
    stg.cargado_en

FROM "postgres"."intermediate"."int_precios_vivienda_unificado" stg

LEFT JOIN "postgres"."core"."dim_tiempo"    dt ON stg.anio = dt.anio AND stg.trimestre = dt.trimestre
LEFT JOIN "postgres"."core"."dim_geografia" dg ON stg.geografia_nombre = dg.geografia_nombre AND stg.nivel_geografico = dg.nivel_geografico