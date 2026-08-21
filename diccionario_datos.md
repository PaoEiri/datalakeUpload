## Anexo A. Diccionario de datos

### Reference

**reference.dim_geografia (BASE TABLE)**

15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | - |
| nombre | text | - |
| codigo_ine | character varying(10) | - |
| es_codigo_oficial_ine | boolean | - |
| nivel | text | - |
| nivel_orden | integer | - |
| codigo_municipio | integer | - |
| codigo_provincia | integer | - |
| codigo_ccaa | integer | - |
| codigo_pais | integer | - |

**reference.seed_geografia_tinsa (BASE TABLE)**

15 filas: mapeo slug de URL Tinsa -> id_geografia

| Columna | Tipo | Descripción |
|---|---|---|
| slug_tinsa | character varying(100) | - |
| id_geografia | integer | - |

**reference.seed_indicadores_fuentes (BASE TABLE)**

37 filas: metadatos de carga (curaduría aplica_municipal/aplica_distrital, concepto_id)

| Columna | Tipo | Descripción |
|---|---|---|
| indicador_id | integer | - |
| descripcion | text | - |
| nombre_indicador | text | - |
| categoria_indicador | text | - |
| unidad | text | - |
| aplica_municipal | boolean | - |
| aplica_distrital | boolean | - |
| es_indice_porcentaje | integer | - |
| tipo_indicador | text | - |
| codigo_ine | integer | - |
| link_fuente | text | - |
| concepto_id | text | - |
| rango_fechas | text | - |
| periodicidad | text | - |
| notas_adaptacion | text | - |
| usar_en_ml | boolean | - |

### Staging

**staging.stg_indicadores_demograficos_ambos (VIEW)**

Normalizado de la tabla INE 31114 (indicadores demográficos, municipal y distrital)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_demograficos_municipio (VIEW)**

Normalizado de la tabla INE 69301 (demográficos actualizados, histórico largo, solo municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_desigualdad_renta (VIEW)**

Normalizado de la tabla INE 31111 (distribución de la renta por unidad de consumo, municipal y distrital)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_fuente_ingreso (VIEW)**

Normalizado de la tabla INE 31107 (distribución por fuente de ingresos)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_gini_p80p20 (VIEW)**

Normalizado de la tabla INE 37706 (Gini y P80/P20, escala 0-100 sin normalizar)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_hogares_vivienda_seguridad (VIEW)**

Normalizado de la tabla INE 69330 (hogares, vivienda y seguridad, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_malaga (VIEW)**

Normalizado de la tabla INE 69303 (indicadores socioeconómicos varios, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_renta_persona_hogar (VIEW)**

Normalizado de la tabla INE 31106 (renta media/mediana)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_turismo (VIEW)**

Normalizado de la tabla INE 69307 (indicadores turísticos, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_indicadores_uso_suelo (VIEW)**

Normalizado de la tabla INE 69333 (uso del suelo y superficie, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(200) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_poblacion_sexo (VIEW)**

Normalizado de la tabla INE 2882 (población por sexo, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | - |
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| nombre_indicador | character varying(50) | - |
| anio | integer | - |
| valor | numeric(18,4) | - |

**staging.stg_precios_tinsa (VIEW)**

Precio €/m² (Tinsa), todos los niveles, con anio/trimestre separados y slug derivado de la URL

| Columna | Tipo | Descripción |
|---|---|---|
| zona | character varying(100) | - |
| anio | integer | - |
| trimestre | integer | - |
| precio_m2 | numeric(18,4) | - |
| url | character varying(300) | - |
| slug_tinsa | text | - |

**staging.stg_transacciones_libre (VIEW)**

Transacciones de vivienda libre, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| tipo_vivienda | text | - |

**staging.stg_transacciones_nueva (VIEW)**

Transacciones de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| tipo_vivienda | text | - |

**staging.stg_transacciones_protegida (VIEW)**

Transacciones de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| tipo_vivienda | text | - |

**staging.stg_transacciones_segunda_mano (VIEW)**

Transacciones de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| tipo_vivienda | text | - |

### Intermediate

**intermediate.int_indicadores_unificado (VIEW)**

Unión de los 8 indicadores INE con id_indicador canónico resuelto (colapsa duplicados multi-fuente) y filtro aplica_municipal/aplica_distrital aplicado

| Columna | Tipo | Descripción |
|---|---|---|
| geografia_codigo_ine | text | - |
| nivel_geografico | text | - |
| anio | integer | - |
| valor | numeric(18,4) | - |
| id_indicador | integer | - |

**intermediate.int_precios_vivienda_unificado (VIEW)**

Precios €/m² de Tinsa con id_geografia resuelto vía seed_geografia_tinsa (join por slug de URL, nunca por texto de zona)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | - |
| anio | integer | - |
| trimestre | integer | - |
| precio_m2 | numeric(18,4) | - |

**intermediate.int_transacciones_unificado (VIEW)**

Unión de los 4 tipos de vivienda con id_geografia resuelto (hoy solo Málaga municipio)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| tipo_vivienda | text | - |

### Core

**core.dim_geografia (BASE TABLE)**

Dimensión de geografía (15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | - |
| nombre | text | - |
| codigo_ine | character varying(10) | - |
| es_codigo_oficial_ine | boolean | - |
| nivel | text | - |
| nivel_orden | integer | - |
| codigo_municipio | integer | - |
| codigo_provincia | integer | - |
| codigo_ccaa | integer | - |
| codigo_pais | integer | - |

**core.dim_indicador (BASE TABLE)**

32 indicadores socioeconómicos del INE, colapsados por concepto_id desde seed_indicadores_fuentes (37 filas)

| Columna | Tipo | Descripción |
|---|---|---|
| id_indicador | integer | - |
| descripcion | text | - |
| nombre_indicador | text | - |
| categoria_indicador | text | - |
| unidad | text | - |
| es_indice_porcentaje | integer | - |
| tipo_indicador | text | - |

**core.dim_modelo (BASE TABLE)**

Registro de modelos de ML entrenados (champion/challenger). Ver src/tasks/ml.py.

| Columna | Tipo | Descripción |
|---|---|---|
| id_modelo | integer | - |
| nombre_modelo | character varying(20) | - |
| version | character varying(50) | - |
| fecha_entrenamiento | timestamp without time zone | - |
| es_champion | boolean | - |
| r2 | numeric(10,6) | - |
| rmse | numeric(18,6) | - |
| mae | numeric(18,6) | - |
| accuracy_direccional | numeric(10,6) | - |
| indicadores_usados | json | - |
| importancia_features | json | - |

**core.dim_tiempo (BASE TABLE)**

Dimensión de tiempo, granularidad trimestral (precios/transacciones) y anual (indicadores). NO usar como Date Table en Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | - |
| anio | integer | - |
| trimestre | integer | - |
| granularidad | text | - |
| fecha | date | - |
| es_futuro | boolean | - |

**core.dim_tipo_vivienda (BASE TABLE)**

4 tipos atómicos de vivienda para transacciones inmobiliarias (sin fila 'total')

| Columna | Tipo | Descripción |
|---|---|---|
| id_tipo_vivienda | integer | - |
| nombre_tipo | text | - |

### Marts

**marts.fact_indicadores_anuales (BASE TABLE)**

Indicadores socioeconómicos del INE por tiempo (anual), geografía e indicador - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | - |
| id_geografia | integer | - |
| id_indicador | integer | - |
| valor | numeric(18,4) | Valor del indicador |

**marts.fact_precio_vivienda (BASE TABLE)**

Precio €/m² (Tinsa) por tiempo y geografía - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | - |
| id_geografia | integer | - |
| precio_m2 | numeric(18,4) | Precio medio €/m² |

**marts.fact_predicciones (BASE TABLE)**

Predicciones del modelo champion de precio_m2 por tiempo, geografía y modelo - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | - |
| id_geografia | integer | - |
| id_modelo | integer | - |
| id_prediccion | integer | - |
| precio_predicho | numeric(18,4) | Precio €/m² predicho (backtesting o forecast, ver es_forecast) |
| intervalo_inferior | numeric(18,4) | - |
| intervalo_superior | numeric(18,4) | - |
| es_forecast | boolean | - |
| creado_en | timestamp without time zone | - |

**marts.fact_transacciones_inmobiliarias (BASE TABLE)**

Número de transacciones inmobiliarias por tiempo, geografía (municipio) y tipo de vivienda - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | - |
| id_geografia | integer | - |
| id_tipo_vivienda | integer | - |
| num_transacciones | integer | Número de transacciones inmobiliarias |

### Otros

**staging.ine_demograficos_ambos (BASE TABLE)**

INE tabla 31114 — Indicadores demográficos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Distritos | character varying(150) | - |
| Secciones | character varying(150) | - |
| Indicadores demograficos | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_demograficos_municipio (BASE TABLE)**

INE tabla 69301 — Indicadores demográficos actualizados (histórico más largo), solo municipal de Málaga (sin desglose distrital), filtrado a Sexo=Total

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Indicadores | character varying(200) | - |
| Sexo | character varying(50) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_desigualdad_renta (BASE TABLE)**

INE tabla 31111 — Distribución de la renta por unidad de consumo, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Distritos | character varying(150) | - |
| Secciones | character varying(150) | - |
| Distribucion de la renta por unidad de consumo | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |
| Sexo | character varying(50) | - |

**staging.ine_fuente_ingreso (BASE TABLE)**

INE tabla 31107 — Distribución por fuente de ingresos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Distritos | character varying(150) | - |
| Secciones | character varying(150) | - |
| Distribucion por fuente de ingresos | character varying(200) | - |
| Periodo | character varying(10) | - |
| valor_porcentaje | character varying(50) | Columna original '% distribucion de fuentes de ingreso' |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_gini_p80p20 (BASE TABLE)**

INE tabla 37706 — Índice de Gini y distribución de la renta P80/P20, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Distritos | character varying(150) | - |
| Secciones | character varying(150) | - |
| Indice de Gini y Distribucion de la renta P80/P20 | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_hogares_vivienda_seguridad (BASE TABLE)**

INE tabla 69330 — Hogares, vivienda y seguridad, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Indicadores | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_indicadores_malaga (BASE TABLE)**

INE tabla 69303 — Indicadores socioeconómicos varios, municipal de Málaga (texto plano, sin código INE)

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Indicadores | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_poblacion_sexo (BASE TABLE)**

INE tabla 2882 — Población por sexo, municipal de Málaga (sin distrito/sección)

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Sexo | character varying(50) | Total, Hombres o Mujeres |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_renta_persona_hogar (BASE TABLE)**

INE tabla 31106 — Renta neta media por persona y por hogar, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Distritos | character varying(150) | - |
| Secciones | character varying(150) | - |
| Indicadores de renta media y mediana | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_turismo (BASE TABLE)**

INE tabla 69307 — Indicadores turísticos, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Indicadores | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_uso_suelo (BASE TABLE)**

INE tabla 69333 — Uso del suelo y superficie, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| Municipios | character varying(150) | - |
| Indicadores | character varying(200) | - |
| Periodo | character varying(10) | - |
| Total | character varying(50) | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**public.ml_model_registry (BASE TABLE)**

Registro de modelos entrenados (champion/challenger). Ver dbt/models/core/dim_modelo.sql.

| Columna | Tipo | Descripción |
|---|---|---|
| id_modelo | integer | - |
| version | character varying(50) | - |
| algoritmo | character varying(20) | 'naive', 'ridge' o 'xgboost' |
| fecha_entrenamiento | timestamp without time zone | - |
| hiperparametros | json | - |
| r2 | numeric(10,6) | - |
| accuracy_direccional | numeric(10,6) | - |
| rmse | numeric(18,6) | - |
| mae | numeric(18,6) | - |
| es_champion | boolean | - |
| ruta_minio_modelo | character varying(300) | - |
| ruta_minio_shap | character varying(300) | - |
| indicadores_usados | json | - |
| importancia_features | json | - |

**public.predicciones_ml_raw (BASE TABLE)**

Predicciones del modelo champion de precio_m2 (variación trimestral), backtesting + forecast recursivo, antes de resolver id_tiempo. Ver dbt/models/marts/fact_predicciones.sql.

| Columna | Tipo | Descripción |
|---|---|---|
| id_prediccion | integer | - |
| id_geografia | integer | - |
| anio | integer | - |
| trimestre | integer | - |
| id_modelo | integer | FK a ml_model_registry |
| precio_predicho | numeric(18,4) | - |
| intervalo_inferior | numeric(18,4) | - |
| intervalo_superior | numeric(18,4) | - |
| es_forecast | boolean | - |
| creado_en | timestamp without time zone | - |

**staging.tinsa_precios (BASE TABLE)**

Precio €/m² (Tinsa), todos los niveles geográficos (país/CCAA/provincia/municipio/distrito), identificados por URL

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| zona | character varying(100) | Nombre de la zona (ambiguo, NO usar para geografía — ver url) |
| periodo | character varying(20) | Formato 'YYYY QT', ej. '2021 4T' |
| valor | numeric(18,4) | Precio €/m², ya en formato numérico estándar (punto decimal) |
| url | character varying(300) | URL completa de scraping; el slug tras /precio-vivienda/ identifica la geografía vía seed_geografia_tinsa |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_libre (BASE TABLE)**

Transacciones inmobiliarias de vivienda libre, municipio de Málaga (Ministerio de Transportes y Movilidad Sostenible)

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_nueva (BASE TABLE)**

Transacciones inmobiliarias de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_protegida (BASE TABLE)**

Transacciones inmobiliarias de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_segunda_mano (BASE TABLE)**

Transacciones inmobiliarias de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | - |
| municipio | character varying(100) | - |
| anio | smallint | - |
| trimestre | smallint | - |
| num_transacciones | integer | - |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**reporting.v_indicadores_cobertura (VIEW)**

Vista de diagnóstico (no de negocio): años con dato real vs rango declarado en el seed, por indicador y nivel geográfico. Incluye indicadores activos e inactivos, para decidir manualmente (vía aplica_municipal/aplica_distrital en reference.seed_indicadores_fuentes) qué indicadores tienen datos suficientes antes de la siguiente carga.

| Columna | Tipo | Descripción |
|---|---|---|
| indicador_id | integer | - |
| nombre_indicador | text | - |
| categoria_indicador | text | - |
| codigo_ine | integer | - |
| nivel_geografico | text | - |
| aplica_actualmente | boolean | - |
| rango_declarado | text | - |
| anio_min_real | integer | - |
| anio_max_real | integer | - |
| anios_con_dato | bigint | - |
| anios_esperados | integer | - |
| cobertura_pct | numeric | - |


---
*Diccionario generado automáticamente a partir de catalog.json y manifest.json (50 relaciones documentadas).*
