

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'protegida' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_protegida"