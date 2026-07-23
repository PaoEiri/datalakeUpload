

SELECT
    zona            AS geografia_nombre,
    nivel_geografico,
    anio,
    trimestre,
    fecha,
    valor           AS precio_m2,
    fuente,
    cargado_en
FROM "postgres"."staging"."tinsa_precios_vivienda"
WHERE fecha IS NOT NULL