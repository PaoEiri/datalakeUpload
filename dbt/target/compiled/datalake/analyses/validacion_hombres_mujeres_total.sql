-- Query de apoyo (no es un test dbt) para inspeccionar manualmente la
-- prueba de calidad Hombres + Mujeres = Población total-m por año.
SELECT
    anio,
    MAX(CASE WHEN nombre_indicador = 'Hombres' THEN valor END) AS hombres,
    MAX(CASE WHEN nombre_indicador = 'Mujeres' THEN valor END) AS mujeres,
    MAX(CASE WHEN nombre_indicador = 'Total' THEN valor END) AS total,
    MAX(CASE WHEN nombre_indicador = 'Hombres' THEN valor END)
        + MAX(CASE WHEN nombre_indicador = 'Mujeres' THEN valor END) AS suma_hombres_mujeres
FROM "postgres"."staging"."stg_poblacion_sexo"
GROUP BY anio
ORDER BY anio