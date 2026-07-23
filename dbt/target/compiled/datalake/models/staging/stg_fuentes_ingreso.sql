

SELECT
    COALESCE("Distritos", "Municipios") AS geografia_nombre,
    CASE
        WHEN "Distritos" IS NOT NULL THEN 'DISTRITO'
        ELSE 'MUNICIPIO'
    END AS nivel_geografico,
    fuente_ingreso AS nombre_indicador,
    CAST("Periodo" AS INTEGER) AS anio,
    CAST(REPLACE("Total", ',', '.') AS NUMERIC) AS valor
FROM "postgres"."staging"."fuentes_ingreso"
WHERE "Secciones" IS NULL