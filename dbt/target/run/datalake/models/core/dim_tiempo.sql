
  
    

  create  table "postgres"."core"."dim_tiempo__dbt_tmp"
  
  
    
  
  (
    id_tiempo bigint not null,
    anio integer not null,
    trimestre integer,
    granularidad text not null,
    fecha date,
    es_futuro boolean,
    
    primary key (id_tiempo)
    )
 ;
    insert into "postgres"."core"."dim_tiempo__dbt_tmp" (
      id_tiempo, anio, trimestre, granularidad, fecha, es_futuro
    )
  
  (
    
    select id_tiempo, anio, trimestre, granularidad, fecha, es_futuro
    from (
        

-- NO marcar como "Date Table" en Power BI: mezcla granularidad trimestral
-- (precios/transacciones) y anual (indicadores).
WITH real_trimestral AS (
    SELECT DISTINCT anio, trimestre FROM "postgres"."intermediate"."int_precios_vivienda_unificado"
    UNION
    SELECT DISTINCT anio, trimestre FROM "postgres"."intermediate"."int_transacciones_unificado"
),

max_trimestral AS (
    SELECT MAX(
        MAKE_DATE(anio, CASE trimestre WHEN 1 THEN 1 WHEN 2 THEN 4 WHEN 3 THEN 7 WHEN 4 THEN 10 END, 1)
    ) AS fecha_max
    FROM real_trimestral
),

-- Trimestres futuros sin dato real todavía, para que fact_predicciones
-- (pipeline de ML, src/tasks/ml.py) pueda resolver id_tiempo por join igual
-- que el resto de las fact tables, en vez de guardar anio/trimestre propios.
-- 12 trimestres (3 años) de margen sobre el horizonte de forecast actual del
-- pipeline (FORECAST_TRIMESTRES=6 en src/tasks/ml.py) — no hace falta tocar
-- este modelo si ese horizonte cambia, mientras siga por debajo de 12.
futuros AS (
    SELECT
        EXTRACT(YEAR FROM d)::int AS anio,
        EXTRACT(QUARTER FROM d)::int AS trimestre
    FROM max_trimestral,
         generate_series(fecha_max + INTERVAL '3 months', fecha_max + INTERVAL '3 months' * 12, INTERVAL '3 months') AS d
),

periodos AS (
    SELECT anio, trimestre FROM real_trimestral
    UNION
    SELECT DISTINCT anio, CAST(NULL AS INT) AS trimestre FROM "postgres"."intermediate"."int_indicadores_unificado"
    UNION
    SELECT anio, trimestre FROM futuros
)

SELECT
    ROW_NUMBER() OVER (ORDER BY anio, trimestre NULLS FIRST) AS id_tiempo,
    anio,
    trimestre,
    CASE WHEN trimestre IS NULL THEN 'Anual' ELSE 'Trimestral' END AS granularidad,
    CASE
        WHEN trimestre IS NULL THEN MAKE_DATE(anio, 1, 1)
        ELSE MAKE_DATE(anio, CASE trimestre WHEN 1 THEN 1 WHEN 2 THEN 4 WHEN 3 THEN 7 WHEN 4 THEN 10 END, 1)
    END AS fecha,
    -- Calculado de forma uniforme para todas las filas (no solo las
    -- sintéticas de "futuros"). OJO: esta tabla es materialized='table', se
    -- recalcula solo en cada dbt run — un trimestre marcado es_futuro=TRUE
    -- puede quedar desactualizado (ya pasado en el calendario real) hasta
    -- el siguiente dbt run.
    (CASE
        WHEN trimestre IS NULL THEN MAKE_DATE(anio, 1, 1)
        ELSE MAKE_DATE(anio, CASE trimestre WHEN 1 THEN 1 WHEN 2 THEN 4 WHEN 3 THEN 7 WHEN 4 THEN 10 END, 1)
    END) > CURRENT_DATE AS es_futuro
FROM periodos
WHERE anio IS NOT NULL
ORDER BY anio, trimestre NULLS FIRST
    ) as model_subq
  );
  