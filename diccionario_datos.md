## Anexo A. Diccionario de datos

**Nota sobre integridad referencial**: las columnas marcadas **[PK]**, **[FK → esquema.tabla]** o **[UNIQUE]** tienen esa constraint aplicada físicamente en PostgreSQL (no solo validada por tests de dbt). En `reference` se agregó por SQL directo (tablas no reconstruidas por dbt); en `core`/`marts` se declaró vía `constraints:` + `config.contract.enforced: true` en los `schema.yml` de dbt, por lo que persiste en cada `dbt run` (dbt genera el `CREATE TABLE` con las constraints incluidas).

### Reference

**reference.dim_geografia (BASE TABLE)**

15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | Identificador único de la geografía **[PK]** |
| nombre | text | Nombre de la geografía (ej. "Málaga (Municipio)", "Bailén-Miraflores") |
| codigo_ine | character varying(10) | Código INE oficial de la geografía |
| es_codigo_oficial_ine | boolean | Indica si codigo_ine es un código INE real y verificable (false para distritos, que no tienen código INE oficial propio) |
| nivel | text | Nivel geográfico: "Distrito", "Municipio", "Provincia", "Comunidad Autónoma" o "País" |
| nivel_orden | integer | Orden jerárquico del nivel geográfico, de menor a mayor extensión |
| codigo_municipio | integer | Código INE del municipio al que pertenece esta geografía |
| codigo_provincia | integer | Código INE de la provincia a la que pertenece esta geografía |
| codigo_ccaa | integer | Código INE de la comunidad autónoma a la que pertenece esta geografía |
| codigo_pais | integer | Código del país al que pertenece esta geografía |

**reference.seed_geografia_tinsa (BASE TABLE)**

15 filas: mapeo slug de URL Tinsa -> id_geografia

| Columna | Tipo | Descripción |
|---|---|---|
| slug_tinsa | character varying(100) | Fragmento de la URL de Tinsa que identifica la zona (clave de join, no el nombre de texto libre) **[UNIQUE, admite NULL — la fila de España no tiene slug propio]** |
| id_geografia | integer | Geografía a la que corresponde ese slug **[PK, FK → reference.dim_geografia]** |

**reference.seed_indicadores_fuentes (BASE TABLE)**

80 filas: metadatos de carga (curaduría aplica_municipal/aplica_distrital, concepto_id)

| Columna | Tipo | Descripción |
|---|---|---|
| indicador_id | integer | Identificador único del indicador **[PK]** |
| descripcion | text | Descripción editable del indicador, gestionada desde la pestaña "Indicadores" de la UI |
| nombre_indicador | text | Nombre del indicador tal como lo publica el INE |
| categoria_indicador | text | Categoría temática del indicador (ej. socioeconómico, demográfico, vivienda, turismo) |
| unidad | text | Unidad de medida del indicador (ej. Euros, Porcentaje, Número) |
| aplica_municipal | boolean | Si el indicador está activo a nivel municipal (visible en Power BI y en la UI) |
| aplica_distrital | boolean | Si el indicador está activo a nivel distrital |
| es_indice_porcentaje | integer | Si el valor se expresa como porcentaje (1) o como cantidad absoluta (0) |
| tipo_indicador | text | Clasificación adicional del tipo de indicador |
| codigo_ine | integer | Código de la tabla INE de origen (ej. 31106, 69303) |
| link_fuente | text | URL de la fuente original en el INE |
| concepto_id | text | Identificador de concepto usado para colapsar en un mismo id_indicador canónico los duplicados que distintas fuentes publican del mismo concepto |
| rango_fechas | text | Rango de años declarado como disponible para este indicador |
| periodicidad | text | Frecuencia de publicación del indicador (habitualmente "Anual") |
| notas_adaptacion | text | Notas de curaduría manual sobre el indicador, editables desde la UI |
| usar_en_ml | boolean | Si el indicador se usa como feature en el pipeline de Machine Learning (ver Pipeline de Machine Learning) |

### Staging

**staging.stg_indicadores_demograficos_ambos (VIEW)**

Normalizado de la tabla INE 31114 (indicadores demográficos, municipal y distrital)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (31114) |
| geografia_codigo_ine | text | Código INE de la geografía (municipio o distrito), tal como lo publica el INE en la fuente original |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato (los indicadores INE se publican con periodicidad anual) |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y geografía |

**staging.stg_indicadores_demograficos_municipio (VIEW)**

Normalizado de la tabla INE 69301 (demográficos actualizados, histórico largo, solo municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (69301) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE en la fuente original |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_indicadores_desigualdad_renta (VIEW)**

Normalizado de la tabla INE 31111 (distribución de la renta por unidad de consumo, municipal y distrital)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (31111) |
| geografia_codigo_ine | text | Código INE de la geografía (municipio o distrito), tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y geografía |

**staging.stg_indicadores_fuente_ingreso (VIEW)**

Normalizado de la tabla INE 31107 (distribución por fuente de ingresos)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (31107) |
| geografia_codigo_ine | text | Código INE de la geografía (municipio o distrito), tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y geografía |

**staging.stg_indicadores_gini_p80p20 (VIEW)**

Normalizado de la tabla INE 37706 (Gini y P80/P20, escala 0-100 sin normalizar)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (37706) |
| geografia_codigo_ine | text | Código INE de la geografía (municipio o distrito), tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y geografía |

**staging.stg_indicadores_hogares_vivienda_seguridad (VIEW)**

Normalizado de la tabla INE 69330 (hogares, vivienda y seguridad, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (69330) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_indicadores_malaga (VIEW)**

Normalizado de la tabla INE 69303 (indicadores socioeconómicos varios, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (69303) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_indicadores_renta_persona_hogar (VIEW)**

Normalizado de la tabla INE 31106 (renta media/mediana)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (31106) |
| geografia_codigo_ine | text | Código INE de la geografía (municipio o distrito), tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y geografía |

**staging.stg_indicadores_turismo (VIEW)**

Normalizado de la tabla INE 69307 (indicadores turísticos, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (69307) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_indicadores_uso_suelo (VIEW)**

Normalizado de la tabla INE 69333 (uso del suelo y superficie, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (69333) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(200) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_poblacion_sexo (VIEW)**

Normalizado de la tabla INE 2882 (población por sexo, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_ine_fuente | integer | Código de la tabla INE de origen de este indicador (2882) |
| geografia_codigo_ine | text | Código INE del municipio, tal como lo publica el INE |
| nivel_geografico | text | Nivel geográfico del dato (siempre "Municipio" en esta fuente) |
| nombre_indicador | character varying(50) | Nombre del indicador tal como aparece en la fuente INE original |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador para ese año y municipio |

**staging.stg_precios_tinsa (VIEW)**

Precio €/m² (Tinsa), todos los niveles, con anio/trimestre separados y slug derivado de la URL

| Columna | Tipo | Descripción |
|---|---|---|
| zona | character varying(100) | Nombre de la zona publicado por Tinsa (texto libre, no usar como clave — usar slug_tinsa) |
| anio | integer | Año del dato |
| trimestre | integer | Trimestre del dato (1 a 4) |
| precio_m2 | numeric(18,4) | Precio medio por metro cuadrado (€/m²) publicado por Tinsa |
| url | character varying(300) | URL completa de origen del dato en Tinsa |
| slug_tinsa | text | Fragmento de la URL que identifica la zona (usado para resolver id_geografia vía seed_geografia_tinsa) |

**staging.stg_transacciones_libre (VIEW)**

Transacciones de vivienda libre, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| tipo_vivienda | text | Tipo de vivienda (constante "libre" en esta vista) |

**staging.stg_transacciones_nueva (VIEW)**

Transacciones de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| tipo_vivienda | text | Tipo de vivienda (constante "nueva" en esta vista) |

**staging.stg_transacciones_protegida (VIEW)**

Transacciones de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| tipo_vivienda | text | Tipo de vivienda (constante "protegida" en esta vista) |

**staging.stg_transacciones_segunda_mano (VIEW)**

Transacciones de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| tipo_vivienda | text | Tipo de vivienda (constante "segunda_mano" en esta vista) |

### Intermediate

**intermediate.int_indicadores_unificado (VIEW)**

Unión de los 8 indicadores INE con id_indicador canónico resuelto (colapsa duplicados multi-fuente) y filtro aplica_municipal/aplica_distrital aplicado

| Columna | Tipo | Descripción |
|---|---|---|
| geografia_codigo_ine | text | Código INE de la geografía, pendiente de resolver a id_geografia |
| nivel_geografico | text | Nivel geográfico del dato: "Municipio" o "Distrito" |
| anio | integer | Año del dato |
| valor | numeric(18,4) | Valor numérico del indicador |
| id_indicador | integer | Identificador del indicador ya resuelto a su forma canónica (colapsa duplicados de distintas fuentes que miden el mismo concepto, vía concepto_id) |

**intermediate.int_precios_vivienda_unificado (VIEW)**

Precios €/m² de Tinsa con id_geografia resuelto vía seed_geografia_tinsa (join por slug de URL, nunca por texto de zona)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | FK a dim_geografia, ya resuelto vía seed_geografia_tinsa |
| anio | integer | Año del dato |
| trimestre | integer | Trimestre del dato (1 a 4) |
| precio_m2 | numeric(18,4) | Precio medio por metro cuadrado (€/m²) |

**intermediate.int_transacciones_unificado (VIEW)**

Unión de los 4 tipos de vivienda con id_geografia resuelto (hoy solo Málaga municipio)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | FK a dim_geografia (hoy siempre Málaga municipio) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias |
| tipo_vivienda | text | Tipo de vivienda: libre, nueva, protegida o segunda mano |

### Core

**core.dim_geografia (BASE TABLE)**

Dimensión de geografía (15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España)

| Columna | Tipo | Descripción |
|---|---|---|
| id_geografia | integer | Identificador único de la geografía **[PK]** |
| nombre | text | Nombre de la geografía (ej. "Málaga (Municipio)", "Bailén-Miraflores") |
| codigo_ine | character varying(10) | Código INE oficial de la geografía |
| es_codigo_oficial_ine | boolean | Indica si codigo_ine es un código INE real y verificable (false para distritos, que no tienen código INE oficial propio) |
| nivel | text | Nivel geográfico: "Distrito", "Municipio", "Provincia", "Comunidad Autónoma" o "País" |
| nivel_orden | integer | Orden jerárquico del nivel geográfico, de menor a mayor extensión |
| codigo_municipio | integer | Código INE del municipio al que pertenece esta geografía |
| codigo_provincia | integer | Código INE de la provincia a la que pertenece esta geografía |
| codigo_ccaa | integer | Código INE de la comunidad autónoma a la que pertenece esta geografía |
| codigo_pais | integer | Código del país al que pertenece esta geografía |

**core.dim_indicador (BASE TABLE)**

78 indicadores socioeconómicos del INE, colapsados por concepto_id desde seed_indicadores_fuentes (80 filas)

| Columna | Tipo | Descripción |
|---|---|---|
| id_indicador | integer | Identificador único del indicador, canónico tras colapsar duplicados **[PK]** |
| descripcion | text | Descripción del indicador |
| nombre_indicador | text | Nombre del indicador tal como lo publica el INE |
| categoria_indicador | text | Categoría temática del indicador |
| unidad | text | Unidad de medida del indicador |
| es_indice_porcentaje | integer | Si el valor se expresa como porcentaje (1) o como cantidad absoluta (0) |
| tipo_indicador | text | Clasificación adicional del tipo de indicador |

**core.dim_modelo (BASE TABLE)**

Registro de modelos de ML entrenados (champion/challenger). Ver src/tasks/ml.py.

| Columna | Tipo | Descripción |
|---|---|---|
| id_modelo | integer | Identificador único del modelo entrenado **[PK]** |
| nombre_modelo | character varying(20) | Algoritmo del modelo: 'naive', 'ridge' o 'xgboost' |
| version | character varying(50) | Identificador de versión del modelo (timestamp de entrenamiento + algoritmo) |
| fecha_entrenamiento | timestamp without time zone | Fecha y hora en que se entrenó el modelo |
| es_champion | boolean | Si es el modelo actualmente activo sirviendo predicciones |
| r2 | numeric(10,6) | Coeficiente de determinación (R²) obtenido en la validación walk-forward |
| rmse | numeric(18,6) | Raíz del error cuadrático medio (walk-forward, sobre la variación trimestral del precio) |
| mae | numeric(18,6) | Error absoluto medio (walk-forward, sobre la variación trimestral del precio) |
| accuracy_direccional | numeric(10,6) | Proporción de trimestres donde el modelo acertó la dirección (sube/baja) de la variación del precio |
| indicadores_usados | json | Lista de los indicadores socioeconómicos usados como features en este modelo (id + nombre) |
| importancia_features | json | Peso/coeficiente de cada feature del modelo, ordenado por magnitud descendente |

**core.dim_tiempo (BASE TABLE)**

Dimensión de tiempo, granularidad trimestral (precios/transacciones) y anual (indicadores). NO usar como Date Table en Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | Identificador único del periodo **[PK]** |
| anio | integer | Año del periodo |
| trimestre | integer | Trimestre del periodo (1 a 4); NULL para periodos de granularidad anual |
| granularidad | text | Granularidad del periodo: "trimestral" o "anual" |
| fecha | date | Fecha representativa del periodo (fin de trimestre o de año) |
| es_futuro | boolean | Si el periodo es posterior a la fecha actual, incluye los trimestres sintéticos generados para el horizonte de forecast del modelo de ML |

**core.dim_tipo_vivienda (BASE TABLE)**

4 tipos atómicos de vivienda para transacciones inmobiliarias (sin fila 'total')

| Columna | Tipo | Descripción |
|---|---|---|
| id_tipo_vivienda | integer | Identificador único del tipo de vivienda **[PK]** |
| nombre_tipo | text | Nombre del tipo de vivienda: libre, nueva, protegida o segunda mano |

### Marts

**marts.fact_indicadores_anuales (BASE TABLE)**

Indicadores socioeconómicos del INE por tiempo (anual), geografía e indicador - lista para Power BI. Restricción **UNIQUE** sobre (id_tiempo, id_geografia, id_indicador) — el grano de la tabla.

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | **[FK → core.dim_tiempo]** (granularidad anual) |
| id_geografia | bigint | **[FK → core.dim_geografia]** |
| id_indicador | integer | **[FK → core.dim_indicador]** |
| valor | numeric(18,4) | Valor del indicador |

**marts.fact_precio_vivienda (BASE TABLE)**

Precio €/m² (Tinsa) por tiempo y geografía - lista para Power BI. Restricción **UNIQUE** sobre (id_tiempo, id_geografia) — el grano de la tabla.

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | **[FK → core.dim_tiempo]** (granularidad trimestral) |
| id_geografia | integer | **[FK → core.dim_geografia]** |
| precio_m2 | numeric(18,4) | Precio medio €/m² |

**marts.fact_predicciones (BASE TABLE)**

Predicciones del modelo champion de precio_m2 por tiempo, geografía y modelo - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | **[FK → core.dim_tiempo]** (trimestre al que corresponde la predicción) |
| id_geografia | integer | **[FK → core.dim_geografia]** (hoy siempre Málaga municipio) |
| id_modelo | integer | **[FK → core.dim_modelo]** — modelo que generó la predicción |
| id_prediccion | integer | Identificador único de la fila de predicción **[PK]** |
| precio_predicho | numeric(18,4) | Precio €/m² predicho (backtesting o forecast, ver es_forecast) |
| intervalo_inferior | numeric(18,4) | Límite inferior del intervalo de confianza de la predicción |
| intervalo_superior | numeric(18,4) | Límite superior del intervalo de confianza de la predicción |
| es_forecast | boolean | Si es un trimestre de forecast puro (true, sin dato real de precio todavía) o de backtesting (false, con dato real disponible para comparar) |
| creado_en | timestamp without time zone | Fecha y hora en que se generó la predicción |

**marts.fact_transacciones_inmobiliarias (BASE TABLE)**

Número de transacciones inmobiliarias por tiempo, geografía (municipio) y tipo de vivienda - lista para Power BI. Restricción **UNIQUE** sobre (id_tiempo, id_geografia, id_tipo_vivienda) — el grano de la tabla.

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | bigint | **[FK → core.dim_tiempo]** |
| id_geografia | integer | **[FK → core.dim_geografia]** |
| id_tipo_vivienda | integer | **[FK → core.dim_tipo_vivienda]** |
| num_transacciones | integer | Número de transacciones inmobiliarias |

### Otros

**staging.ine_demograficos_ambos (BASE TABLE)**

INE tabla 31114 — Indicadores demográficos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Distritos | character varying(150) | Nombre del distrito tal como lo publica el INE (texto original) |
| Secciones | character varying(150) | Sección censal (texto original, no usada en este proyecto) |
| Indicadores demograficos | character varying(200) | Nombre del indicador demográfico (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_demograficos_municipio (BASE TABLE)**

INE tabla 69301 — Indicadores demográficos actualizados (histórico más largo), solo municipal de Málaga (sin desglose distrital), filtrado a Sexo=Total

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Indicadores | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Sexo | character varying(50) | Sexo del dato (filtrado a "Total" en el modelo staging correspondiente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_desigualdad_renta (BASE TABLE)**

INE tabla 31111 — Distribución de la renta por unidad de consumo, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Distritos | character varying(150) | Nombre del distrito tal como lo publica el INE (texto original) |
| Secciones | character varying(150) | Sección censal (texto original, no usada en este proyecto) |
| Distribucion de la renta por unidad de consumo | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |
| Sexo | character varying(50) | Sexo del dato (texto original de la fuente) |

**staging.ine_fuente_ingreso (BASE TABLE)**

INE tabla 31107 — Distribución por fuente de ingresos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Distritos | character varying(150) | Nombre del distrito tal como lo publica el INE (texto original) |
| Secciones | character varying(150) | Sección censal (texto original, no usada en este proyecto) |
| Distribucion por fuente de ingresos | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| valor_porcentaje | character varying(50) | Columna original '% distribucion de fuentes de ingreso' |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_gini_p80p20 (BASE TABLE)**

INE tabla 37706 — Índice de Gini y distribución de la renta P80/P20, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Distritos | character varying(150) | Nombre del distrito tal como lo publica el INE (texto original) |
| Secciones | character varying(150) | Sección censal (texto original, no usada en este proyecto) |
| Indice de Gini y Distribucion de la renta P80/P20 | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_hogares_vivienda_seguridad (BASE TABLE)**

INE tabla 69330 — Hogares, vivienda y seguridad, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Indicadores | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_indicadores_malaga (BASE TABLE)**

INE tabla 69303 — Indicadores socioeconómicos varios, municipal de Málaga (texto plano, sin código INE)

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Indicadores | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_poblacion_sexo (BASE TABLE)**

INE tabla 2882 — Población por sexo, municipal de Málaga (sin distrito/sección)

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Sexo | character varying(50) | Total, Hombres o Mujeres |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_renta_persona_hogar (BASE TABLE)**

INE tabla 31106 — Renta neta media por persona y por hogar, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Distritos | character varying(150) | Nombre del distrito tal como lo publica el INE (texto original) |
| Secciones | character varying(150) | Sección censal (texto original, no usada en este proyecto) |
| Indicadores de renta media y mediana | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_turismo (BASE TABLE)**

INE tabla 69307 — Indicadores turísticos, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Indicadores | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.ine_uso_suelo (BASE TABLE)**

INE tabla 69333 — Uso del suelo y superficie, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| Municipios | character varying(150) | Nombre del municipio tal como lo publica el INE (texto original) |
| Indicadores | character varying(200) | Nombre del indicador (texto original de la fuente) |
| Periodo | character varying(10) | Año de publicación (texto original) |
| Total | character varying(50) | Valor del indicador (texto original, sin normalizar) |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**public.ml_model_registry (BASE TABLE)**

Registro de modelos entrenados (champion/challenger). Ver dbt/models/core/dim_modelo.sql.

| Columna | Tipo | Descripción |
|---|---|---|
| id_modelo | integer | Identificador único del modelo entrenado **[PK]** |
| version | character varying(50) | Identificador de versión del modelo (timestamp de entrenamiento + algoritmo) |
| algoritmo | character varying(20) | 'naive', 'ridge' o 'xgboost' |
| fecha_entrenamiento | timestamp without time zone | Fecha y hora en que se entrenó el modelo |
| hiperparametros | json | Hiperparámetros ganadores del modelo (ej. alpha de Ridge) |
| r2 | numeric(10,6) | Coeficiente de determinación (R²) obtenido en la validación walk-forward |
| accuracy_direccional | numeric(10,6) | Proporción de trimestres donde el modelo acertó la dirección (sube/baja) de la variación del precio |
| rmse | numeric(18,6) | Raíz del error cuadrático medio (walk-forward, sobre la variación trimestral del precio) |
| mae | numeric(18,6) | Error absoluto medio (walk-forward, sobre la variación trimestral del precio) |
| es_champion | boolean | Si es el modelo actualmente activo sirviendo predicciones |
| ruta_minio_modelo | character varying(300) | Ruta del archivo .pkl del modelo serializado, almacenado en MinIO |
| ruta_minio_shap | character varying(300) | Ruta del gráfico de explicabilidad (SHAP para XGBoost, coeficientes estandarizados para Ridge), almacenado en MinIO |
| indicadores_usados | json | Lista de los indicadores socioeconómicos usados como features en este modelo (id + nombre) |
| importancia_features | json | Peso/coeficiente de cada feature del modelo, ordenado por magnitud descendente |

**public.predicciones_ml_raw (BASE TABLE)**

Predicciones del modelo champion de precio_m2 (variación trimestral), backtesting + forecast recursivo, antes de resolver id_tiempo. Ver dbt/models/marts/fact_predicciones.sql.

| Columna | Tipo | Descripción |
|---|---|---|
| id_prediccion | integer | Identificador único de la fila de predicción **[PK]** |
| id_geografia | integer | FK a dim_geografia (hoy siempre Málaga municipio) |
| anio | integer | Año del trimestre predicho |
| trimestre | integer | Trimestre predicho (1 a 4) |
| id_modelo | integer | **[FK → public.ml_model_registry]** |
| precio_predicho | numeric(18,4) | Precio €/m² predicho para ese trimestre |
| intervalo_inferior | numeric(18,4) | Límite inferior del intervalo de confianza de la predicción |
| intervalo_superior | numeric(18,4) | Límite superior del intervalo de confianza de la predicción |
| es_forecast | boolean | Si es un trimestre de forecast puro (true, sin dato real de precio todavía) o de backtesting (false, con dato real disponible para comparar) |
| creado_en | timestamp without time zone | Fecha y hora en que se generó la predicción |

**staging.tinsa_precios (BASE TABLE)**

Precio €/m² (Tinsa), todos los niveles geográficos (país/CCAA/provincia/municipio/distrito), identificados por URL

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
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
| id | integer | Identificador autogenerado de la fila |
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_nueva (BASE TABLE)**

Transacciones inmobiliarias de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_protegida (BASE TABLE)**

Transacciones inmobiliarias de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**staging.transacciones_segunda_mano (BASE TABLE)**

Transacciones inmobiliarias de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| id | integer | Identificador autogenerado de la fila |
| municipio | character varying(100) | Nombre del municipio (texto original de la fuente) |
| anio | smallint | Año de la transacción |
| trimestre | smallint | Trimestre de la transacción (1 a 4) |
| num_transacciones | integer | Número de transacciones inmobiliarias registradas |
| creado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a actualizado_en, no hay UPDATE de filas) |
| actualizado_en | timestamp without time zone | Timestamp de la carga TRUNCATE+INSERT (igual a creado_en, no hay UPDATE de filas) |

**reporting.v_indicadores_cobertura (VIEW)**

Vista de diagnóstico (no de negocio): años con dato real vs rango declarado en el seed, por indicador y nivel geográfico. Incluye indicadores activos e inactivos, para decidir manualmente (vía aplica_municipal/aplica_distrital en reference.seed_indicadores_fuentes) qué indicadores tienen datos suficientes antes de la siguiente carga.

| Columna | Tipo | Descripción |
|---|---|---|
| indicador_id | integer | FK a seed_indicadores_fuentes |
| nombre_indicador | text | Nombre del indicador |
| categoria_indicador | text | Categoría temática del indicador |
| codigo_ine | integer | Código de la tabla INE de origen |
| nivel_geografico | text | Nivel geográfico evaluado: "Municipio" o "Distrito" |
| aplica_actualmente | boolean | Si el indicador está activo actualmente para ese nivel (aplica_municipal/aplica_distrital) |
| rango_declarado | text | Rango de años declarado como disponible en el seed |
| anio_min_real | integer | Primer año con dato real publicado |
| anio_max_real | integer | Último año con dato real publicado |
| anios_con_dato | bigint | Cantidad de años con dato real publicado |
| anios_esperados | integer | Cantidad de años esperados según el rango declarado |
| cobertura_pct | numeric | Porcentaje de cobertura real (anios_con_dato / anios_esperados) |


---
*Diccionario generado automáticamente a partir de catalog.json y manifest.json (50 relaciones documentadas), con descripciones completadas manualmente.*
