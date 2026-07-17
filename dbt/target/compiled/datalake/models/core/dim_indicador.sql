

SELECT
    ROW_NUMBER() OVER (ORDER BY indicador) AS id_indicador,
    indicador                               AS nombre_indicador,
    CASE indicador
        WHEN 'Índice'                       THEN 'indice_base'
        WHEN 'Variación anual'              THEN 'variacion'
        WHEN 'Variación trimestral'         THEN 'variacion'
        WHEN 'Variación en lo que va de año' THEN 'variacion'
        ELSE 'otro'
    END AS tipo_indicador
FROM (
    SELECT DISTINCT indicador
    FROM "postgres"."staging"."ipv_precios_vivienda"
    WHERE indicador IS NOT NULL
) t