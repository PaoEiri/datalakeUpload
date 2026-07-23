# Especificación de carga de datos — TFM Data Warehouse Mercado Inmobiliario Málaga

Este documento consolida TODAS las reglas de estructura, filtrado y limpieza
acordadas para las fuentes de datos del proyecto. Es la referencia única para
generar/actualizar los modelos `staging/` de dbt. No inventar columnas ni
reglas no descritas aquí — si algo no está cubierto, preguntar antes de
asumir.

---

## Reglas transversales (aplican a TODAS las fuentes salvo excepción explícita)

1. **Filtro de municipio**: siempre Málaga, pero el formato exacto de
   comparación varía por archivo (ver tabla de fuentes más abajo). Nunca usar
   comparación insensible a mayúsculas (no `LOWER()`/`ILIKE`) salvo que se
   indique lo contrario — comparación exacta, case-sensitive, con `trim()`.

2. **Conversión numérica estándar español** (miles con `.`, decimal con `,`):
   ```sql
   cast(replace(replace(trim(valor_raw), '.', ''), ',', '.') as numeric(18,4))
   ```
   Aplicar SIEMPRE a fuentes del INE y del Ministerio (tienen formato
   español). **Excepción: Tinsa** ya viene en formato numérico estándar
   internacional (punto decimal), NO aplicar esta conversión ahí.

3. **Columna `Secciones`** (cuando exista en el archivo origen): filtrar
   siempre por vacío/NULL. Es un nivel de granularidad más fino que distrito
   que no se usa en este proyecto.

4. **Nunca cargar filas "Total" agregadas cuando existen las categorías
   atómicas que las componen** (antipatrón de doble conteo). Aplica a:
   - Transacciones inmobiliarias: NO cargar
     `min_Transacciones_vivienda_malaga.xlsx` (es la suma de los 4 tipos).
     Cargar solo los 4 archivos por tipo (libre, segunda mano, nueva,
     protegida); el total se calcula siempre en tiempo de consulta
     (`SUM` sin filtro de tipo).
   - `dim_tipo_vivienda` no debe contener una fila "total".

---

## dim_geografia (ya cerrada, 15 filas + 0 reservado sin usar)

`id_geografia`: 0 = reservado/sin usar (Kimball "Desconocido", no se crea
fila aún) | 1-11 = distritos | 12 = Málaga Provincia | 13 = Andalucía |
14 = España | **15 = Málaga Municipio** (id cambiado desde el 0 original a
propósito, por buenas prácticas de modelado — todo el modelo se reconstruye
desde cero, no hay que preservar compatibilidad con `nroZona=0` del proyecto
anterior).

Columnas: `id_geografia, nombre, codigo_ine, es_codigo_oficial_ine, nivel,
nivel_orden, codigo_municipio, codigo_provincia, codigo_ccaa, codigo_pais`.
`es_codigo_oficial_ine = FALSE` solo para nivel Distrito (código sintético
propio, no oficial INE). Autoreferencia: cada fila lleva también su propio
código en la columna de su nivel (ej. la fila Provincia lleva
`codigo_provincia` relleno).

CSV ya generado y entregado: `dim_geografia.csv`.

---

## seed_geografia_tinsa (tabla de correspondencia, 15 filas, verificada)

Necesaria porque Tinsa identifica geografía por URL, no por código INE.

| slug_tinsa (ruta tras `/precio-vivienda/`) | id_geografia |
|---|---|
| *(vacío, raíz)* | 14 |
| `andalucia` | 13 |
| `andalucia/malaga` | 12 |
| `andalucia/malaga/malaga` | 15 |
| `andalucia/malaga/malaga/bailen-miraflores` | 4 |
| `andalucia/malaga/malaga/campanillas` | 9 |
| `andalucia/malaga/malaga/carretera-de-cadiz` | 7 |
| `andalucia/malaga/malaga/centro` | 1 |
| `andalucia/malaga/malaga/churriana` | 8 |
| `andalucia/malaga/malaga/ciudad-jardin` | 3 |
| `andalucia/malaga/malaga/cruz-de-humilladero` | 6 |
| `andalucia/malaga/malaga/este` | 2 |
| `andalucia/malaga/malaga/palma-palmilla` | 5 |
| `andalucia/malaga/malaga/puerto-de-la-torre` | 10 |
| `andalucia/malaga/malaga/teatinos-universidad` | 11 |

Todas las URLs verificadas contra el listado real usado en el scraping.

---

## seed_indicadores_fuentes (37 filas) → dim_indicador (32 filas, colapsada)

Dos tablas con roles distintos (NO fusionar):
- `seed_indicadores_fuentes.csv`: metadatos de carga (qué archivo/código INE
  corresponde a cada fila, si aplica a municipal/distrital). Uso: pipeline.
  **Archivo ya generado y entregado.**
- `dim_indicador` (modelo dbt, `core/dim_indicador.sql`, ya entregado):
  colapsa por `concepto_id` a 32 filas de negocio limpias, sin duplicados
  visibles. Uso: Power BI / usuario final.

Columnas del seed: `indicador_id, descripcion, nombre_indicador,
categoria_indicador, unidad, aplica_municipal, aplica_distrital,
es_indice_porcentaje, tipo_indicador, codigo_ine, link_fuente, concepto_id`.

`aplica_municipal` / `aplica_distrital`: NO son "existe el dato a ese nivel",
son "esta fila concreta es la que se debe USAR para ese nivel" (bandera de
selección/curaduría). Cuando varias fuentes miden el mismo concepto
(`concepto_id` compartido), solo una fila debe tener `TRUE` por nivel; el
resto queda documentado pero inactivo (ambas columnas en `FALSE`), NUNCA se
borran filas.

Grupos con `concepto_id` (multi-fuente) ya resueltos:
- `poblacion_total`: activo distrital=id 8 (31114), activo municipal=id 32
  (69301, más reciente); id 29 (2882) documentado, inactivo.
- `poblacion_65mas`: distrital=id 15 (31114), municipal=id 33 (69301).
- `poblacion_nacional`: distrital=id 14 (31114), municipal=id 34 (69301).
- `renta_persona`: municipal+distrital=id 1 (31106, fuente preferida);
  id 38 (69303) documentado, inactivo.

Prueba de calidad de datos recomendada (Anexo A / dbt test): Hombres +
Mujeres = Población total-m, ya que el INE los publica como filas separadas
del mismo indicador base (fuente 2882) y deberían sumar exactamente.

Índice de Gini (`id=5`): el INE lo publica en escala 0-100 (NO 0-1 estándar
internacional). Se mantiene en la escala nativa del INE, sin normalizar.
`tipo_indicador = "índice(0-100)"`.

---

## dim_tipo_vivienda

Solo 4 tipos atómicos: `libre`, `segunda mano`, `nueva`, `protegida`. NO
incluir "total" (ver regla transversal nº4).

---

## Inventario de fuentes: estructura y filtros por archivo

### Indicadores INE (formato largo: 1 fila = 1 indicador x año, alimentan `seed_indicadores_fuentes` / `fact_indicadores_anuales`)

| Archivo | Formato columna Municipios | Columnas extra | Filtro |
|---|---|---|---|
| `31106.csv` | `"29067 Málaga"` (código+nombre) | `Distritos`, `Secciones` | `Municipios="29067 Málaga"` + (`Distritos` vacío = municipal, o código `290670X` = distrito) + `Secciones` vacío |
| `31114.csv` | `"29067 Málaga"` | `Distritos`, `Secciones` | igual que 31106 |
| `31107.csv` | `"29067 Málaga"` | `Distritos`, `Secciones` | igual que 31106 |
| `37706.csv` | `"29067 Málaga"` | `Distritos`, `Secciones` | igual que 31106. Índice de Gini en escala 0-100 (ver arriba) |
| `2882.csv` | `"29067 Málaga"` | `Sexo` (Total/Hombres/Mujeres) | `Municipios="29067 Málaga"`, sin distrito/sección (no existen esas columnas). `Sexo` mapea a 3 indicadores: Total→id 29, Hombres→id 10, Mujeres→id 11. Serie hasta 2025 (más reciente que el resto) |
| `69303.csv` | `"Málaga"` (texto plano, SIN código) | — | `Municipios="Málaga"` |
| `69301.csv` | `"Málaga"` (texto plano) | `Sexo` | `Municipios="Málaga"` + `Sexo="Total"`. Solo municipal (no tiene distrito). Serie hasta 2024/2010 histórico más largo que el resto |
| `69307.csv` | `"Málaga"` (texto plano) | — | `Municipios="Málaga"`. Valores grandes (miles/millones), ojo con la conversión de miles |

Columna `Total Nacional` (aparece en 69303/69301/69307): rótulo fijo sin
valor informativo, descartar siempre.

Test de rango por `tipo_indicador` (seed): `porcentaje` → 0-100;
`cantidad` → sin techo fijo; `índice(0-100)` → 0-100 (Gini);
`valor >1` → validar rango específico (P80/P20 típicamente 1-5).

### Tinsa (precio de vivienda, alimenta `fact_precio_vivienda`)

Archivo: `tinsa_malaga_andalucia.csv`. Columnas: `zona, periodo, valor, url`.

- `zona` es AMBIGUA por sí sola (ej. "Málaga" aparece como provincia Y como
  municipio) → identificar geografía SIEMPRE por la URL, nunca por `zona`.
- Contar segmentos de la URL tras `/precio-vivienda/` da el nivel (0=País,
  1=CCAA, 2=Provincia, 3=Municipio, 4=Distrito), coincide con `nivel_orden`
  de `dim_geografia`.
- Join contra `seed_geografia_tinsa` por el slug completo (ruta tras
  `/precio-vivienda/`) para obtener `id_geografia` — NO cruzar por texto de
  `zona` contra `dim_geografia.nombre` (los slugs no llevan tildes y hay
  ambigüedad de nombres repetidos entre niveles).
- `periodo` formato `"2021 4T"` → separar en `anio` (int) y `trimestre`
  (int, 1-4).
- `valor`: YA viene en formato numérico estándar (punto decimal) — NO
  aplicar la conversión de coma española aquí.

### Transacciones inmobiliarias (Ministerio, alimentan `fact_transacciones_inmobiliarias`)

Archivos: `min_Transacciones inmobiliarias de vivienda {libre|segunda mano|
nueva|protegida} por municipios.XLS`. Los 4 tienen idéntica estructura.

**NO cargar** `min_Transacciones inmobiliarias de vivienda malaga.xlsx` (es
la suma de los 4 anteriores, ver regla transversal nº4).

Estructura (tabla ancha, jerarquía por FILAS, no por columnas):
- Columna B: nombre de fila. Puede ser cabecera de Comunidad Autónoma
  (ej. "ANDALUCÍA"), cabecera de Provincia (ej. "Málaga" en negrita, SIN
  datos numéricos a la derecha), o fila de Municipio (ej. "Málaga" en fila
  distinta, CON datos numéricos completos).
- **Distinguir cabecera de provincia vs. fila de municipio por presencia de
  datos, NO por texto** (el nombre "Málaga" se repite para provincia y
  municipio en filas distintas — no se puede diferenciar solo por string).
- Método: recorrido secuencial fila por fila, manteniendo una variable
  `provincia_actual` que se actualiza cada vez que se detecta una fila-
  cabecera de provincia (texto en col. B + todas las columnas de datos
  vacías). Las filas de municipio que siguen heredan `provincia_actual`
  hasta la siguiente cabecera.
- Filtro final: `provincia_actual = "Málaga"` AND `texto_columna_B =
  "Málaga"` AND fila tiene datos (esto aísla la fila de municipio, no la de
  cabecera).
- Encabezado de columnas a 2 niveles: años en celda combinada (abarca 4
  columnas de trimestre) + fila de trimestre (1º-4º) debajo. Hay que
  "propagar hacia la derecha" el año a sus 4 columnas de trimestre antes de
  poder pivotar a formato largo.
- Transformar de ancho a largo: 1 fila por (año, trimestre, num_transacciones).
- Nota de calidad (documentar en Anexo A, SIN tratamiento especial en los
  datos — no se añade columna `es_provisional`): el dato del año actual,
  primer trimestre, es provisional según la fuente del Ministerio.

---

## Pendientes / decisiones abiertas (no resueltas en esta sesión)

- Confirmar si hace falta ajustar el rango `[Año] >= 2015` fijo en las
  medidas DAX de correlación, dado que algunas fuentes (69301, 2882) tienen
  historial más largo (hasta 2010) que podría aprovecharse en el futuro.
- ~~Revisar y actualizar cualquier referencia a `nroZona=0`~~ — verificado:
  no queda ninguna en código; `dataset/dim_geografia.csv` sí traía
  `id_geografia=0` para Málaga Municipio (contradiciendo este documento) y
  se corrigió en `dbt/seeds` → `reference.dim_geografia` a **15**, como aquí
  se especifica.
- ~~Catálogo de fuentes + versionado (`fuentes_registradas`,
  `fuentes_registradas_historial`, `vigente`)~~ — implementado. Ver
  `fuentes_registradas_y_api.md` y `consideraciones_prefect_flows.md` para
  el diseño, ya construido en `infra/docker-entrypoint-initdb.d/04_fuentes_registradas.sql`,
  `src/api/fuentes.py` y `flows/dataset_management.py`.
