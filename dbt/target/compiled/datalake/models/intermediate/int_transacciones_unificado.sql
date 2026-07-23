

-- UNION de los 4 tipos atómicos. NUNCA se incluye el fichero "total"
-- (min_Transacciones...malaga.xlsx) — antipatrón de doble conteo, ver
-- especificacion_carga_datos_TFM.md regla transversal nº4.
-- Hoy solo produce id_geografia del municipio de Málaga; preparado para
-- más geografías si el Ministerio publica desglose distrital en el futuro.
WITH union_transacciones AS (
    SELECT * FROM "postgres"."staging"."stg_transacciones_libre"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_transacciones_segunda_mano"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_transacciones_nueva"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_transacciones_protegida"
)

SELECT
    sdg.id_geografia,
    ut.anio,
    ut.trimestre,
    ut.num_transacciones,
    ut.tipo_vivienda
FROM union_transacciones ut
LEFT JOIN "postgres"."reference"."dim_geografia" sdg
    ON ut.municipio = 'Málaga' AND sdg.nombre = 'Málaga (Municipio)'