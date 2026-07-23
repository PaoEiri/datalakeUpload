-- Prueba de calidad: Hombres + Mujeres debe igualar Población total-m
-- (fuente 2882, tres filas del mismo indicador base). Ver
-- especificacion_carga_datos_TFM.md.
WITH pivot AS (
    SELECT
        anio,
        MAX(CASE WHEN nombre_indicador = 'Hombres' THEN valor END) AS hombres,
        MAX(CASE WHEN nombre_indicador = 'Mujeres' THEN valor END) AS mujeres,
        MAX(CASE WHEN nombre_indicador = 'Total' THEN valor END) AS total
    FROM "postgres"."staging"."stg_poblacion_sexo"
    GROUP BY anio
)
SELECT *
FROM pivot
WHERE ROUND(COALESCE(hombres, 0) + COALESCE(mujeres, 0), 2) != ROUND(COALESCE(total, 0), 2)