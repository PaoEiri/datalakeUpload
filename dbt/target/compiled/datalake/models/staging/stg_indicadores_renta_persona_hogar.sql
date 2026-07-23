

SELECT
    31106 AS codigo_ine_fuente,
    CASE WHEN "Distritos" IS NOT NULL THEN LEFT("Distritos", 7) ELSE LEFT("Municipios", 5) END AS geografia_codigo_ine,
    CASE WHEN "Distritos" IS NOT NULL THEN 'DISTRITO' ELSE 'MUNICIPIO' END AS nivel_geografico,
    "Indicadores de renta media y mediana" AS nombre_indicador,
    TRIM("Periodo")::int AS anio,
    CAST(REPLACE(REPLACE(TRIM("Total"), '.', ''), ',', '.') AS NUMERIC(18, 4)) AS valor
FROM "postgres"."staging"."ine_renta_persona_hogar"
WHERE TRIM("Municipios") = '29067 Málaga'
  AND ("Secciones" IS NULL OR TRIM("Secciones") = '')