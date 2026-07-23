# Esquema en estrella final — modelo semántico Power BI

Este es el diseño definitivo, resultado de toda la sesión de rediseño. Es lo
que debe reflejar el modelo de datos de Power BI una vez Claude Code termine
de regenerar el proyecto dbt.

## Dimensiones

### dim_tiempo
| Columna | Tipo | Nota |
|---|---|---|
| `id_tiempo` (PK) | INT | |
| `anio` | INT | |
| `trimestre` | INT | NULL en grano anual (indicadores) |
| `granularidad` | STRING | "Trimestral" / "Anual" |
| `fecha` | DATE | primer día del periodo. NO marcar como "Date Table" en Power BI (mezcla granularidades) |

### dim_geografia
| Columna | Tipo | Nota |
|---|---|---|
| `id_geografia` (PK) | INT | 0=reservado sin usar · 1-11=distritos · 12=Málaga Provincia · 13=Andalucía · 14=España · **15=Málaga Municipio** |
| `nombre` | STRING | |
| `codigo_ine` | STRING | |
| `es_codigo_oficial_ine` | BOOLEAN | FALSE solo en Distrito |
| `nivel` | STRING | Municipio/Distrito/Provincia/CCAA/País |
| `nivel_orden` | INT | 1=País … 5=Distrito |
| `codigo_municipio` | STRING | autoreferenciada |
| `codigo_provincia` | STRING | autoreferenciada |
| `codigo_ccaa` | STRING | autoreferenciada |
| `codigo_pais` | STRING | autoreferenciada en todas las filas |

### dim_tipo_vivienda
| Columna | Tipo | Nota |
|---|---|---|
| `id_tipo_vivienda` (PK) | INT | |
| `tipo_vivienda` | STRING | solo 4 valores: libre / segunda mano / nueva / protegida. **Sin fila "total"** |

### dim_indicador
| Columna | Tipo | Nota |
|---|---|---|
| `id_indicador` (PK) | INT | 32 filas, ya colapsadas (sin duplicados de fuente) |
| `nombre_negocio` | STRING | nombre limpio, visible al usuario |
| `categoria_indicador` | STRING | socioeconómico / demográfico / turismo / desigualdad |
| `unidad` | STRING | €, %, persona, ‰, edad, # ... |
| `es_indice_porcentaje` | BOOLEAN | para formato automático en Power BI |
| `tipo_indicador` | STRING | cantidad / porcentaje / índice(0-100) / valor >1 |
| `concepto_id` | STRING (nullable) | trazabilidad interna; NO usar en Power BI |

## Tablas de hechos

### fact_precio_vivienda
Grano: 1 fila por (tiempo, geografía). Cubre **todos** los niveles (municipio, distrito, provincia, CCAA, país) porque Tinsa los publica todos.

| Columna | Tipo |
|---|---|
| `id_tiempo` (FK) | INT |
| `id_geografia` (FK) | INT |
| `precio_m2` | DECIMAL |

### fact_transacciones_inmobiliarias
Grano: 1 fila por (tiempo, geografía, tipo de vivienda). Hoy solo `id_geografia = 15` (Málaga municipio) tiene datos; el esquema queda abierto a distrito/otras ciudades a futuro.

| Columna | Tipo |
|---|---|
| `id_tiempo` (FK) | INT |
| `id_geografia` (FK) | INT |
| `id_tipo_vivienda` (FK) | INT |
| `num_transacciones` | INT |

*El "total" de transacciones se calcula siempre como `SUM(num_transacciones)` sin filtrar tipo — nunca existe como fila propia.*

### fact_indicadores_anuales
Grano: 1 fila por (tiempo, geografía, indicador). `trimestre` de `dim_tiempo` siempre NULL aquí (grano anual).

| Columna | Tipo |
|---|---|
| `id_tiempo` (FK) | INT |
| `id_geografia` (FK) | INT |
| `id_indicador` (FK) | INT |
| `valor` | DECIMAL |

## Relaciones (todas 1 a muchos, dimensión → hecho)

| Dimensión | fact_precio_vivienda | fact_transacciones_inmobiliarias | fact_indicadores_anuales |
|---|:---:|:---:|:---:|
| dim_tiempo | ✅ | ✅ | ✅ |
| dim_geografia | ✅ | ✅ | ✅ |
| dim_tipo_vivienda | — | ✅ | — |
| dim_indicador | — | — | ✅ |

Todas las relaciones activas, cardinalidad 1:N, filtro de dimensión → hecho (dirección única, como es estándar en un esquema en estrella).
