

-- Colapsa seed_indicadores_fuentes (37 filas) a 32 filas de negocio vía
-- concepto_id: cuando varias fuentes miden el mismo concepto, se conserva
-- una sola fila (el indicador_id mínimo del grupo). Ver
-- especificacion_carga_datos_TFM.md.
WITH canonico AS (
    SELECT
        indicador_id,
        descripcion,
        nombre_indicador,
        categoria_indicador,
        unidad,
        es_indice_porcentaje,
        -- El INE publica el Gini en escala 0-100 (no 0-1 estándar
        -- internacional); se corrige aquí la etiqueta, el dato ya venía
        -- crudo en su escala nativa.
        CASE WHEN indicador_id = 5 THEN 'índice(0-100)' ELSE tipo_indicador END AS tipo_indicador,
        concepto_id,
        CASE
            WHEN concepto_id IS NOT NULL THEN MIN(indicador_id) OVER (PARTITION BY concepto_id)
            ELSE indicador_id
        END AS id_indicador_canonico
    FROM "postgres"."reference"."seed_indicadores_fuentes"
)

SELECT
    id_indicador_canonico AS id_indicador,
    descripcion,
    nombre_indicador,
    categoria_indicador,
    unidad,
    es_indice_porcentaje,
    tipo_indicador
FROM canonico
WHERE indicador_id = id_indicador_canonico