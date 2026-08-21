
  create view "postgres"."reporting"."v_indicadores_cobertura__dbt_tmp"
    
    
  as (
    

-- Vista de diagnóstico (no de negocio): cobertura real de datos por indicador
-- y nivel geográfico, para decidir manualmente (vía aplica_municipal/
-- aplica_distrital en reference.seed_indicadores_fuentes) qué indicadores
-- tienen datos suficientes antes de la siguiente carga/análisis de
-- correlación. Incluye también indicadores actualmente inactivos, para
-- poder reconsiderarlos. No aplica el filtro aplica_municipal/aplica_distrital
-- que sí usa int_indicadores_unificado.sql — aquí se muestra como columna
-- informativa (aplica_actualmente), no como filtro.
WITH union_indicadores AS (
    SELECT * FROM "postgres"."staging"."stg_indicadores_renta_persona_hogar"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_demograficos_ambos"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_fuente_ingreso"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_gini_p80p20"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_poblacion_sexo"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_malaga"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_demograficos_municipio"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_turismo"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_uso_suelo"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_hogares_vivienda_seguridad"
    UNION ALL
    SELECT * FROM "postgres"."staging"."stg_indicadores_desigualdad_renta"
),

datos AS (
    SELECT
        s.indicador_id,
        s.nombre_indicador,
        s.categoria_indicador,
        s.codigo_ine,
        s.rango_fechas,
        ui.nivel_geografico,
        CASE WHEN ui.nivel_geografico = 'MUNICIPIO' THEN s.aplica_municipal ELSE s.aplica_distrital END AS aplica_actualmente,
        ui.anio,
        ui.valor
    FROM union_indicadores ui
    INNER JOIN "postgres"."reference"."seed_indicadores_fuentes" s
        ON ui.codigo_ine_fuente = s.codigo_ine
       AND ui.nombre_indicador = s.nombre_indicador
),

anios_rango AS (
    SELECT
        *,
        NULLIF(SPLIT_PART(rango_fechas, '-', 1), '')::int AS anio_desde_declarado,
        NULLIF(SPLIT_PART(rango_fechas, '-', 2), '')::int AS anio_hasta_declarado
    FROM datos
)

SELECT
    indicador_id,
    nombre_indicador,
    categoria_indicador,
    codigo_ine,
    nivel_geografico,
    bool_or(aplica_actualmente) AS aplica_actualmente,
    rango_fechas AS rango_declarado,
    MIN(anio) FILTER (WHERE valor IS NOT NULL) AS anio_min_real,
    MAX(anio) FILTER (WHERE valor IS NOT NULL) AS anio_max_real,
    COUNT(DISTINCT anio) FILTER (WHERE valor IS NOT NULL) AS anios_con_dato,
    (MAX(anio_hasta_declarado) - MAX(anio_desde_declarado) + 1) AS anios_esperados,
    ROUND(
        COUNT(DISTINCT anio) FILTER (WHERE valor IS NOT NULL)::numeric
        / NULLIF(MAX(anio_hasta_declarado) - MAX(anio_desde_declarado) + 1, 0) * 100
    , 1) AS cobertura_pct
FROM anios_rango
GROUP BY indicador_id, nombre_indicador, categoria_indicador, codigo_ine, nivel_geografico, rango_fechas
ORDER BY cobertura_pct ASC NULLS LAST, indicador_id
  );