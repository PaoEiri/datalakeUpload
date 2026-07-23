{{ config(materialized='view') }}

-- Modelo más complejo del proyecto: concentra la resolución de duplicados
-- multi-fuente (concepto_id) y la curaduría aplica_municipal/aplica_distrital
-- de seed_indicadores_fuentes. Ver especificacion_carga_datos_TFM.md.
WITH union_indicadores AS (
    SELECT * FROM {{ ref('stg_indicadores_renta_persona_hogar') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_demograficos') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_fuente_ingreso') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_gini_p80p20') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_poblacion_sexo') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_malaga') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_demograficos_actualizado') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_indicadores_turismo') }}
),

-- id_indicador canónico: para conceptos con varias fuentes (concepto_id),
-- se usa el indicador_id mínimo del grupo (mismo criterio que dim_indicador).
fuentes_canonico AS (
    SELECT
        indicador_id,
        codigo_ine,
        nombre_indicador,
        aplica_municipal,
        aplica_distrital,
        CASE
            WHEN concepto_id IS NOT NULL THEN MIN(indicador_id) OVER (PARTITION BY concepto_id)
            ELSE indicador_id
        END AS id_indicador_canonico
    FROM {{ source('reference', 'seed_indicadores_fuentes') }}
)

SELECT
    ui.geografia_codigo_ine,
    ui.nivel_geografico,
    ui.anio,
    ui.valor,
    f.id_indicador_canonico AS id_indicador
FROM union_indicadores ui
INNER JOIN fuentes_canonico f
    ON ui.codigo_ine_fuente = f.codigo_ine
   AND ui.nombre_indicador = f.nombre_indicador
WHERE ((ui.nivel_geografico = 'MUNICIPIO' AND f.aplica_municipal)
    OR (ui.nivel_geografico = 'DISTRITO' AND f.aplica_distrital))
  AND ui.valor IS NOT NULL  -- algunos años quedan sin publicar todavía en la fuente INE
