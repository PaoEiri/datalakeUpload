

SELECT
    zona,
    TRIM(SPLIT_PART(periodo, ' ', 1))::int AS anio,
    TRIM(REPLACE(SPLIT_PART(periodo, ' ', 2), 'T', ''))::int AS trimestre,
    valor AS precio_m2,
    url,
    RTRIM(REGEXP_REPLACE(url, '^.*/precio-vivienda/', ''), '/') AS slug_tinsa
FROM "postgres"."staging"."tinsa_precios"