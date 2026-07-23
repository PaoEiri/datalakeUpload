

SELECT
    COALESCE("Distritos", "Municipios") AS geografia_nombre,
    CASE
        WHEN "Distritos" IS NOT NULL THEN 'DISTRITO'
        ELSE 'MUNICIPIO'
    END AS nivel_geografico,
    "Índice de Gini y Distribución de la renta P80/P20" AS nombre_indicador,
    CAST("Periodo" AS INTEGER) AS anio,
    CAST(REPLACE("Total", ',', '.') AS NUMERIC) AS valor
FROM "postgres"."staging"."gini_p20_distritos"
WHERE "Secciones" IS NULL