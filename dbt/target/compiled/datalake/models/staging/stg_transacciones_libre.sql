

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'libre' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_libre"