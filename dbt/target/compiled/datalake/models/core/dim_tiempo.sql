

SELECT
    ROW_NUMBER() OVER (ORDER BY fecha) AS id_tiempo,
    fecha,
    anio,
    trimestre,
    CONCAT('T', trimestre, ' ', anio)  AS label_periodo,
    CASE trimestre
        WHEN 1 THEN 'Enero - Marzo'
        WHEN 2 THEN 'Abril - Junio'
        WHEN 3 THEN 'Julio - Septiembre'
        WHEN 4 THEN 'Octubre - Diciembre'
    END                                AS descripcion_trimestre
FROM (
    SELECT DISTINCT fecha, anio, trimestre
    FROM "postgres"."staging"."ipv_precios_vivienda"
    WHERE fecha IS NOT NULL
) t
ORDER BY fecha