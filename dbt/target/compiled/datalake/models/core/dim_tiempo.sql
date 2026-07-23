

-- NO marcar como "Date Table" en Power BI: mezcla granularidad trimestral
-- (precios/transacciones) y anual (indicadores).
WITH periodos AS (
    SELECT DISTINCT anio, trimestre FROM "postgres"."intermediate"."int_precios_vivienda_unificado"
    UNION
    SELECT DISTINCT anio, trimestre FROM "postgres"."intermediate"."int_transacciones_unificado"
    UNION
    SELECT DISTINCT anio, CAST(NULL AS INT) AS trimestre FROM "postgres"."intermediate"."int_indicadores_unificado"
)

SELECT
    ROW_NUMBER() OVER (ORDER BY anio, trimestre NULLS FIRST) AS id_tiempo,
    anio,
    trimestre,
    CASE WHEN trimestre IS NULL THEN 'Anual' ELSE 'Trimestral' END AS granularidad,
    CASE
        WHEN trimestre IS NULL THEN MAKE_DATE(anio, 1, 1)
        ELSE MAKE_DATE(anio, CASE trimestre WHEN 1 THEN 1 WHEN 2 THEN 4 WHEN 3 THEN 7 WHEN 4 THEN 10 END, 1)
    END AS fecha
FROM periodos
WHERE anio IS NOT NULL
ORDER BY anio, trimestre NULLS FIRST