-- Active: 1771867685129@@127.0.0.1@5432@postgres

select * from staging.ipv_precios_vivienda;

SELECT COUNT(*) FROM staging_core.dim_tipo_vivienda;
SELECT nombre_comunidad, label_periodo, nombre_tipo, nombre_indicador, valor
FROM marts.fct_precios_vivienda
WHERE codigo_ine = '13'
AND tipo_indicador = 'variacion'
ORDER BY fecha DESC
LIMIT 5;
