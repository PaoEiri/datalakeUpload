

-- Grano: tiempo (trimestral) x geografía (municipio) x tipo_vivienda -> num_transacciones
-- Hoy solo id_geografia del municipio de Málaga (ver int_transacciones_unificado.sql).
-- Solo FKs + métrica: ver nota de esquema en fact_precio_vivienda.sql.
SELECT
    dt.id_tiempo,
    it.id_geografia,
    dtv.id_tipo_vivienda,
    it.num_transacciones
FROM "postgres"."intermediate"."int_transacciones_unificado" it
LEFT JOIN "postgres"."core"."dim_tiempo"        dt  ON it.anio = dt.anio AND it.trimestre = dt.trimestre
LEFT JOIN "postgres"."core"."dim_tipo_vivienda" dtv ON it.tipo_vivienda = dtv.nombre_tipo