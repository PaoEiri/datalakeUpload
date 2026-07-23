# Estructura del proyecto dbt — regeneración completa

Este documento define la estructura de carpetas/archivos que debe quedar en
`models/` y `seeds/` tras la migración. Complementa (no sustituye) a
`especificacion_carga_datos_TFM.md`, que tiene el detalle de reglas de cada
fuente — este archivo es el mapa de "qué archivo va dónde y para qué sirve".

```
proyecto_dbt/
│
├── seeds/                                    # vacío a propósito (ver nota)
│
├── models/
│   ├── core/
│   │   └── sources.yml                      # source 'reference': dim_geografia,
│   │                                         #   seed_geografia_tinsa, seed_indicadores_fuentes
│   ├── staging/
│   │   ├── sources.yml                      # declara las 13 fuentes raw (8 INE + Tinsa + 4 Ministerio)
│   │   ├── schema.yml                       # tests de los modelos staging
│   │   │
│   │   ├── stg_precios_tinsa.sql            # tinsa_malaga_andalucia.csv
│   │   │
│   │   ├── stg_indicadores_renta_persona_hogar.sql   # 31106.csv
│   │   ├── stg_indicadores_demograficos.sql          # 31114.csv
│   │   ├── stg_indicadores_fuente_ingreso.sql        # 31107.csv
│   │   ├── stg_indicadores_gini_p80p20.sql           # 37706.csv
│   │   ├── stg_poblacion_sexo.sql                    # 2882.csv
│   │   ├── stg_indicadores_malaga.sql                # 69303.csv (ya entregado)
│   │   ├── stg_indicadores_demograficos_actualizado.sql  # 69301.csv
│   │   ├── stg_indicadores_turismo.sql               # 69307.csv
│   │   │
│   │   ├── stg_transacciones_libre.sql              # min_..._libre_por_municipios.XLS
│   │   ├── stg_transacciones_segunda_mano.sql       # min_..._segunda_mano_por_municipios.XLS
│   │   ├── stg_transacciones_nueva.sql              # min_..._nueva_por_municipios.XLS
│   │   └── stg_transacciones_protegida.sql          # min_..._protegida_por_municipios.XLS
│   │
│   ├── intermediate/
│   │   ├── schema.yml
│   │   ├── int_precios_vivienda_unificado.sql
│   │   │     -- une stg_precios_tinsa (municipio+distrito+provincia+ccaa+país)
│   │   │     -- resuelve id_geografia vía join con seed_geografia_tinsa
│   │   │
│   │   ├── int_transacciones_unificado.sql
│   │   │     -- UNION de los 4 stg_transacciones_* (libre/2ª mano/nueva/protegida)
│   │   │     -- NUNCA incluye "total" (antipatrón ya resuelto)
│   │   │
│   │   └── int_indicadores_unificado.sql
│   │         -- UNION de los 8 stg_indicadores_* de INE
│   │         -- join contra seed_indicadores_fuentes por nombre_indicador
│   │         -- aplica el filtro aplica_municipal/aplica_distrital para
│   │         --   decidir qué fila usar cuando hay concepto_id compartido
│   │         -- traduce indicador_id de fuente -> id_indicador canónico
│   │         --   (colapsa duplicados: 8/29/32->8, 15/33->15, 14/34->14, 1/38->1)
│   │
│   ├── core/
│   │   ├── schema.yml                       # tests: unique, not_null, accepted_values,
│   │   │                                     #   relationships, + test custom Hombres+Mujeres=Total
│   │   ├── dim_tiempo.sql
│   │   │     -- columnas: id_tiempo, anio, trimestre (NULL en grano anual),
│   │   │        granularidad ('Trimestral'/'Anual'), fecha (DATE)
│   │   │     -- NO marcar como "Date Table" en Power BI (mezcla granularidades)
│   │   │
│   │   ├── dim_geografia.sql                # pass-through del seed (15 filas)
│   │   ├── dim_tipo_vivienda.sql            # 4 filas fijas: libre/segunda mano/nueva/protegida
│   │   └── dim_indicador.sql                # ya entregado, colapsa a 32 filas
│   │
│   └── marts/
│       ├── schema.yml                       # tests de integridad de los 3 hechos
│       ├── fact_precio_vivienda.sql
│       │     -- grano: tiempo x geografia
│       │     -- de int_precios_vivienda_unificado
│       │
│       ├── fact_transacciones_inmobiliarias.sql
│       │     -- grano: tiempo x geografia x tipo_vivienda
│       │     -- de int_transacciones_unificado
│       │     -- hoy solo id_geografia=15 (municipal), preparado para más
│       │
│       └── fact_indicadores_anuales.sql
│             -- grano: tiempo x geografia x indicador
│             -- de int_indicadores_unificado
│             -- id_indicador ya viene canónico (colapsado) desde intermediate
│
└── analyses/ (opcional)
    └── validacion_hombres_mujeres_total.sql   # query de apoyo para el test de calidad
```

## Notas para Claude Code al regenerar

1. **Eliminar del proyecto anterior**: `dim_distritos.sql`, cualquier
   `stg_ventasinmuebles*` o modelo que use el campo de texto `zona` en lugar
   de `id_geografia`, y cualquier referencia a `nroZona`.

2. **Orden de construcción recomendado** (por dependencias): seeds → staging
   (los 13 modelos, sin dependencias entre sí) → intermediate (3 modelos,
   dependen de staging + seeds) → core (4 dimensiones, dependen de seeds/
   staging) → marts (3 hechos, dependen de intermediate + core).

3. **`int_indicadores_unificado.sql` es el modelo más complejo** del
   proyecto — concentra toda la lógica de resolución de duplicados
   (`concepto_id`, `aplica_municipal`/`aplica_distrital`). Priorizarlo y
   testearlo primero, ya que un error ahí se propaga silenciosamente a
   `fact_indicadores_anuales` y de ahí a todas las medidas de correlación de
   Power BI.

4. **Validación obligatoria tras la migración** (ya detallada en
   `especificacion_carga_datos_TFM.md`): recalcular la correlación de
   "€ Renta media por persona" a nivel municipal y verificar que sigue dando
   r ≈ 0,76. Si cambia, hay un error en la migración, no en los datos.

5. Todos los nombres de archivo (`stg_*`) propuestos aquí son sugerencias
   basadas en el contenido de cada fuente — si el proyecto ya tiene una
   convención de nombres distinta establecida, respetarla y renombrar según
   corresponda, manteniendo la lógica descrita en cada bloque.

6. **`dbt/seeds/` queda vacío a propósito** (ver `fuentes_registradas_y_api.md`
   §1): `dim_geografia`, `seed_geografia_tinsa` y `seed_indicadores_fuentes`
   se cargaron una única vez y luego se movieron a tablas normales en el
   esquema `reference` (`ALTER TABLE ... SET SCHEMA reference`), para que un
   `dbt seed` recurrente no las sobrescriba. Los modelos `core/dim_geografia.sql`
   y `dim_indicador.sql`, y los `intermediate/*` que antes hacían
   `{{ ref('seed_*') }}`, ahora hacen `{{ source('reference', ...) }}`
   (declarado en `models/core/sources.yml`). Los 3 CSV originales quedan
   archivados en `dbt/reference_migration/` solo como referencia histórica.

7. **Carpetas reales del proyecto no listadas en el árbol de arriba** (no son
   errores, son adiciones legítimas): `dataset/` (los ficheros fuente reales,
   de solo lectura), `scripts/` (`load_tfm_dataset.py` para el dataset de
   referencia, `generate_data_dictionary.py`), `docs/` (diccionario de datos
   autogenerado), `dbt/tests/` (test custom `assert_hombres_mujeres_igual_total`)
   y `dbt/analyses/`.
