{{ config(materialized='table') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY comunidad) AS id_comunidad,
    comunidad                               AS nombre_comunidad,
    CASE comunidad
        WHEN 'Nacional'           THEN '00'
        WHEN '01 Andalucía'       THEN '01'
        WHEN '02 Aragón'          THEN '02'
        WHEN '03 Asturias, Principado de' THEN '03'
        WHEN '04 Balears, Illes'  THEN '04'
        WHEN '05 Canarias'        THEN '05'
        WHEN '06 Cantabria'       THEN '06'
        WHEN '07 Castilla y León' THEN '07'
        WHEN '08 Castilla - La Mancha' THEN '08'
        WHEN '09 Cataluña'        THEN '09'
        WHEN '10 Comunitat Valenciana' THEN '10'
        WHEN '11 Extremadura'     THEN '11'
        WHEN '12 Galicia'         THEN '12'
        WHEN '13 Madrid, Comunidad de' THEN '13'
        WHEN '14 Murcia, Región de' THEN '14'
        WHEN '15 Navarra, Comunidad Foral de' THEN '15'
        WHEN '16 País Vasco'      THEN '16'
        WHEN '17 Rioja, La'       THEN '17'
        WHEN '18 Ceuta'           THEN '18'
        WHEN '19 Melilla'         THEN '19'
        ELSE 'XX'
    END AS codigo_ine
FROM (
    SELECT DISTINCT comunidad
    FROM {{ source('staging', 'ipv_precios_vivienda') }}
    WHERE comunidad IS NOT NULL
) t