# Diccionario de datos

Generado automáticamente a partir de `dbt/target/manifest.json` y `dbt/target/catalog.json` (`dbt docs generate`). Los tipos de columna provienen del catálogo real de PostgreSQL; las descripciones, de los `schema.yml` del proyecto dbt.

## Staging

### `staging.stg_indicadores_demograficos` (view)

Normalizado de la tabla INE 31114 (indicadores demográficos)

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel_geografico` | text | - |
| `anio` | integer | - |
| `valor` | numeric(18,4) | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nombre_indicador` | character varying(200) | - |

### `staging.stg_indicadores_demograficos_actualizado` (view)

Normalizado de la tabla INE 69301 (demográficos actualizados, histórico largo, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | integer | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nivel_geografico` | text | - |
| `nombre_indicador` | character varying(200) | - |
| `valor` | numeric(18,4) | - |

### `staging.stg_indicadores_fuente_ingreso` (view)

Normalizado de la tabla INE 31107 (distribución por fuente de ingresos)

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel_geografico` | text | - |
| `anio` | integer | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nombre_indicador` | character varying(200) | - |
| `valor` | numeric(18,4) | - |

### `staging.stg_indicadores_gini_p80p20` (view)

Normalizado de la tabla INE 37706 (Gini y P80/P20, escala 0-100 sin normalizar)

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel_geografico` | text | - |
| `anio` | integer | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nombre_indicador` | character varying(200) | - |
| `valor` | numeric(18,4) | - |

### `staging.stg_indicadores_malaga` (view)

Normalizado de la tabla INE 69303 (indicadores socioeconómicos varios, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | integer | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nivel_geografico` | text | - |
| `nombre_indicador` | character varying(200) | - |
| `valor` | numeric(18,4) | - |

### `staging.stg_indicadores_renta_persona_hogar` (view)

Normalizado de la tabla INE 31106 (renta media/mediana)

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel_geografico` | text | - |
| `anio` | integer | - |
| `valor` | numeric(18,4) | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nombre_indicador` | character varying(200) | - |

### `staging.stg_indicadores_turismo` (view)

Normalizado de la tabla INE 69307 (indicadores turísticos, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | integer | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nivel_geografico` | text | - |
| `nombre_indicador` | character varying(200) | - |
| `valor` | numeric(18,4) | - |

### `staging.stg_poblacion_sexo` (view)

Normalizado de la tabla INE 2882 (población por sexo, municipal)

| Columna | Tipo | Descripción |
|---|---|---|
| `nombre_indicador` | character varying(50) | - |
| `anio` | integer | - |
| `valor` | numeric(18,4) | - |
| `codigo_ine_fuente` | integer | - |
| `geografia_codigo_ine` | text | - |
| `nivel_geografico` | text | - |

### `staging.stg_precios_tinsa` (view)

Precio €/m² (Tinsa), todos los niveles, con anio/trimestre separados y slug derivado de la URL

| Columna | Tipo | Descripción |
|---|---|---|
| `anio` | integer | - |
| `trimestre` | integer | - |
| `precio_m2` | numeric(18,4) | - |
| `slug_tinsa` | text | - |
| `zona` | character varying(100) | - |
| `url` | character varying(300) | - |

### `staging.stg_transacciones_libre` (view)

Transacciones de vivienda libre, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo_vivienda` | text | - |
| `num_transacciones` | integer | - |
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |

### `staging.stg_transacciones_nueva` (view)

Transacciones de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo_vivienda` | text | - |
| `num_transacciones` | integer | - |
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |

### `staging.stg_transacciones_protegida` (view)

Transacciones de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo_vivienda` | text | - |
| `num_transacciones` | integer | - |
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |

### `staging.stg_transacciones_segunda_mano` (view)

Transacciones de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `tipo_vivienda` | text | - |
| `num_transacciones` | integer | - |
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |

## Intermediate

### `intermediate.int_indicadores_unificado` (view)

Unión de los 8 indicadores INE con id_indicador canónico resuelto (colapsa duplicados multi-fuente) y filtro aplica_municipal/aplica_distrital aplicado

| Columna | Tipo | Descripción |
|---|---|---|
| `nivel_geografico` | text | - |
| `anio` | integer | - |
| `id_indicador` | integer | - |
| `valor` | numeric(18,4) | - |
| `geografia_codigo_ine` | text | - |

### `intermediate.int_precios_vivienda_unificado` (view)

Precios €/m² de Tinsa con id_geografia resuelto vía seed_geografia_tinsa (join por slug de URL, nunca por texto de zona)

| Columna | Tipo | Descripción |
|---|---|---|
| `id_geografia` | integer | - |
| `anio` | integer | - |
| `trimestre` | integer | - |
| `precio_m2` | numeric(18,4) | - |

### `intermediate.int_transacciones_unificado` (view)

Unión de los 4 tipos de vivienda con id_geografia resuelto (hoy solo Málaga municipio)

| Columna | Tipo | Descripción |
|---|---|---|
| `id_geografia` | integer | - |
| `tipo_vivienda` | text | - |
| `num_transacciones` | integer | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |

## Core (dimensiones)

### `core.dim_geografia` (table)

Dimensión de geografía (15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España)

| Columna | Tipo | Descripción |
|---|---|---|
| `id_geografia` | integer | - |
| `nombre` | text | - |
| `nivel` | text | - |
| `codigo_ine` | character varying(10) | - |
| `es_codigo_oficial_ine` | boolean | - |
| `nivel_orden` | integer | - |
| `codigo_municipio` | integer | - |
| `codigo_provincia` | integer | - |
| `codigo_ccaa` | integer | - |
| `codigo_pais` | integer | - |

### `core.dim_indicador` (table)

32 indicadores socioeconómicos del INE, colapsados por concepto_id desde seed_indicadores_fuentes (37 filas)

| Columna | Tipo | Descripción |
|---|---|---|
| `id_indicador` | integer | - |
| `nombre_indicador` | text | - |
| `descripcion` | text | - |
| `categoria_indicador` | text | - |
| `unidad` | text | - |
| `es_indice_porcentaje` | integer | - |
| `tipo_indicador` | text | - |

### `core.dim_tiempo` (table)

Dimensión de tiempo, granularidad trimestral (precios/transacciones) y anual (indicadores). NO usar como Date Table en Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| `id_tiempo` | bigint | - |
| `anio` | integer | - |
| `granularidad` | text | - |
| `trimestre` | integer | - |
| `fecha` | date | - |

### `core.dim_tipo_vivienda` (table)

4 tipos atómicos de vivienda para transacciones inmobiliarias (sin fila 'total')

| Columna | Tipo | Descripción |
|---|---|---|
| `id_tipo_vivienda` | integer | - |
| `nombre_tipo` | text | - |

## Marts (hechos)

### `marts.fact_indicadores_anuales` (table)

Indicadores socioeconómicos del INE por tiempo (anual), geografía e indicador - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| `id_tiempo` | bigint | - |
| `id_geografia` | integer | - |
| `id_indicador` | integer | - |
| `valor` | numeric(18,4) | Valor del indicador |
| `anio` | integer | - |
| `geografia_nombre` | text | - |
| `nombre_indicador` | text | - |

### `marts.fact_precio_vivienda` (table)

Precio €/m² (Tinsa) por tiempo y geografía - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| `id_tiempo` | bigint | - |
| `id_geografia` | integer | - |
| `precio_m2` | numeric(18,4) | Precio medio €/m² |
| `anio` | integer | - |
| `trimestre` | integer | - |
| `fecha` | date | - |
| `geografia_nombre` | text | - |
| `geografia_nivel` | text | - |

### `marts.fact_transacciones_inmobiliarias` (table)

Número de transacciones inmobiliarias por tiempo, geografía (municipio) y tipo de vivienda - lista para Power BI

| Columna | Tipo | Descripción |
|---|---|---|
| `id_tiempo` | bigint | - |
| `id_geografia` | integer | - |
| `id_tipo_vivienda` | integer | - |
| `num_transacciones` | integer | Número de transacciones inmobiliarias |
| `anio` | integer | - |
| `trimestre` | integer | - |
| `fecha` | date | - |
| `geografia_nombre` | text | - |
| `nombre_tipo` | text | - |

## Fuentes (`sources`)

### `reference.dim_geografia`

15 filas: 11 distritos, Málaga municipio, Málaga provincia, Andalucía, España

| Columna | Tipo | Descripción |
|---|---|---|
| `id_geografia` | integer | - |
| `nombre` | text | - |
| `codigo_ine` | character varying(10) | - |
| `es_codigo_oficial_ine` | boolean | - |
| `nivel` | text | - |
| `nivel_orden` | integer | - |
| `codigo_municipio` | integer | - |
| `codigo_provincia` | integer | - |
| `codigo_ccaa` | integer | - |
| `codigo_pais` | integer | - |

### `staging.ine_demograficos`

INE tabla 31114 — Indicadores demográficos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Distritos` | character varying(150) | - |
| `Secciones` | character varying(150) | - |
| `Indicadores demograficos` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_demograficos_actualizado`

INE tabla 69301 — Indicadores demográficos actualizados (histórico más largo), municipal de Málaga, filtrado a Sexo=Total

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Indicadores` | character varying(200) | - |
| `Sexo` | character varying(50) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_fuente_ingreso`

INE tabla 31107 — Distribución por fuente de ingresos, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Distritos` | character varying(150) | - |
| `Secciones` | character varying(150) | - |
| `Distribucion por fuente de ingresos` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `valor_porcentaje` | character varying(50) | Columna original '% distribucion de fuentes de ingreso' |
| `id` | integer | - |

### `staging.ine_gini_p80p20`

INE tabla 37706 — Índice de Gini y distribución de la renta P80/P20, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Distritos` | character varying(150) | - |
| `Secciones` | character varying(150) | - |
| `Indice de Gini y Distribucion de la renta P80/P20` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_indicadores_malaga`

INE tabla 69303 — Indicadores socioeconómicos varios, municipal de Málaga (texto plano, sin código INE)

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Indicadores` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_poblacion_sexo`

INE tabla 2882 — Población por sexo, municipal de Málaga (sin distrito/sección)

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Sexo` | character varying(50) | Total, Hombres o Mujeres |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_renta_persona_hogar`

INE tabla 31106 — Renta neta media por persona y por hogar, municipal y distrital de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Distritos` | character varying(150) | - |
| `Secciones` | character varying(150) | - |
| `Indicadores de renta media y mediana` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `staging.ine_turismo`

INE tabla 69307 — Indicadores turísticos, municipal de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `Municipios` | character varying(150) | - |
| `Indicadores` | character varying(200) | - |
| `Periodo` | character varying(10) | - |
| `Total` | character varying(50) | - |
| `id` | integer | - |

### `reference.seed_geografia_tinsa`

15 filas: mapeo slug de URL Tinsa -> id_geografia

| Columna | Tipo | Descripción |
|---|---|---|
| `slug_tinsa` | character varying(100) | - |
| `id_geografia` | integer | - |

### `reference.seed_indicadores_fuentes`

37 filas: metadatos de carga (curaduría aplica_municipal/aplica_distrital, concepto_id)

| Columna | Tipo | Descripción |
|---|---|---|
| `indicador_id` | integer | - |
| `descripcion` | text | - |
| `nombre_indicador` | text | - |
| `categoria_indicador` | text | - |
| `unidad` | text | - |
| `aplica_municipal` | boolean | - |
| `aplica_distrital` | boolean | - |
| `es_indice_porcentaje` | integer | - |
| `tipo_indicador` | text | - |
| `codigo_ine` | integer | - |
| `link_fuente` | text | - |
| `concepto_id` | text | - |

### `staging.tinsa_precios`

Precio €/m² (Tinsa), todos los niveles geográficos (país/CCAA/provincia/municipio/distrito), identificados por URL

| Columna | Tipo | Descripción |
|---|---|---|
| `zona` | character varying(100) | Nombre de la zona (ambiguo, NO usar para geografía — ver url) |
| `periodo` | character varying(20) | Formato 'YYYY QT', ej. '2021 4T' |
| `valor` | numeric(18,4) | Precio €/m², ya en formato numérico estándar (punto decimal) |
| `url` | character varying(300) | URL completa de scraping; el slug tras /precio-vivienda/ identifica la geografía vía seed_geografia_tinsa |
| `id` | integer | - |

### `staging.transacciones_libre`

Transacciones inmobiliarias de vivienda libre, municipio de Málaga (Ministerio de Transportes y Movilidad Sostenible)

| Columna | Tipo | Descripción |
|---|---|---|
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |
| `num_transacciones` | integer | - |
| `id` | integer | - |

### `staging.transacciones_nueva`

Transacciones inmobiliarias de vivienda nueva, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |
| `num_transacciones` | integer | - |
| `id` | integer | - |

### `staging.transacciones_protegida`

Transacciones inmobiliarias de vivienda protegida, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |
| `num_transacciones` | integer | - |
| `id` | integer | - |

### `staging.transacciones_segunda_mano`

Transacciones inmobiliarias de vivienda de segunda mano, municipio de Málaga

| Columna | Tipo | Descripción |
|---|---|---|
| `municipio` | character varying(100) | - |
| `anio` | smallint | - |
| `trimestre` | smallint | - |
| `num_transacciones` | integer | - |
| `id` | integer | - |
