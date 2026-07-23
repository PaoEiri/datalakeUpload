

SELECT
    municipio,
    anio,
    trimestre,
    num_transacciones,
    'segunda mano' AS tipo_vivienda
FROM "postgres"."staging"."transacciones_segunda_mano"