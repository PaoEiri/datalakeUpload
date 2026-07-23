

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'nueva' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_nueva"