# Migración a esquema `reference`

Estos 3 CSV **ya no son `dbt seed`** activos (no viven en `dbt/seeds/`). Se
usaron una única vez para poblar `reference.dim_geografia`,
`reference.seed_geografia_tinsa` y `reference.seed_indicadores_fuentes`
(carga inicial vía `dbt seed --full-refresh` + `ALTER TABLE ... SET SCHEMA
reference`). A partir de ahí son tablas Postgres normales, editables
directamente sin riesgo de que un `dbt seed` recurrente las sobrescriba.

Se conservan aquí solo como referencia histórica de la carga inicial. Ver
`fuentes_registradas_y_api.md` (raíz del repo) para el razonamiento completo.
