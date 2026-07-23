

-- Grano: tiempo (anual) x geografía x indicador -> valor
-- id_indicador ya viene canónico (colapsado) desde intermediate.
SELECT
    dt.id_tiempo,
    dg.id_geografia,
    ii.id_indicador,
    dt.anio,
    dg.nombre AS geografia_nombre,
    di.nombre_indicador,
    ii.valor
FROM "postgres"."intermediate"."int_indicadores_unificado" ii
LEFT JOIN "postgres"."core"."dim_tiempo"     dt ON ii.anio = dt.anio AND dt.trimestre IS NULL
LEFT JOIN "postgres"."core"."dim_geografia"  dg ON ii.geografia_codigo_ine = dg.codigo_ine AND UPPER(dg.nivel) = ii.nivel_geografico
LEFT JOIN "postgres"."core"."dim_indicador"  di ON ii.id_indicador = di.id_indicador