

-- Pass-through del seed: dim_geografia ya viene cerrada y verificada
-- (15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía,
-- España). Ver especificacion_carga_datos_TFM.md.
SELECT
    id_geografia,
    nombre,
    codigo_ine,
    es_codigo_oficial_ine,
    nivel,
    nivel_orden,
    codigo_municipio,
    codigo_provincia,
    codigo_ccaa,
    codigo_pais
FROM "postgres"."reference"."dim_geografia"