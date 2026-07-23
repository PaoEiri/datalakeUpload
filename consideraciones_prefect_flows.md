# Consideraciones para reconstruir los flows de Prefect

**Ya implementado — este documento queda como referencia histórica del
diseño.** Dos correcciones sobre lo que se planteó aquí, verificadas contra
el código real antes de construir:
- El flow a extender para Flow 1 no era `flows/02_data_validation.py` (ese
  archivo resultó ser una demo de Prefect sin relación con
  `datasets_upload`, y ya se eliminó del repo) — el flow real es
  `dataset_management_flow` en `flows/dataset_management.py`, que ya
  encadena validación → vigencia → staging → dbt run acotado.
- `flows/03_dbt_run.py` ya aceptaba un selector opcional (`select`) antes
  de esta ronda de trabajo; no hizo falta añadirlo.

Lo demás (`flows/04_staging_manual.py` solo cargaba IPV, había que
construir el dispatcher por fuente desde cero, etc.) se aplicó tal como se
describe abajo. Queda el resto del documento sin editar como registro del
razonamiento original.

No es código todavía — es la lista de requisitos y decisiones que deben
tenerse en cuenta al diseñar los flows nuevos/actualizados, dado todo lo
acordado en `fuentes_registradas_y_api.md` y
`especificacion_carga_datos_TFM.md`.

## Estado actual (según el README) que hay que sustituir/completar

- `flows/04_staging_manual.py` solo carga el histórico IPV
  (`staging.ipv_precios_vivienda`), que ya no tiene modelos dbt asociados.
  No sirve como base para las 12 fuentes reales — hay que construir la
  carga a `staging.*` desde cero para ellas.
- `flows/02_data_validation.py` valida formato/contenido genérico, pero no
  conoce todavía el concepto de `id_fuente` ni el mecanismo de vigencia
  (`vigente`) — hay que extenderlo.
- `flows/03_dbt_run.py` corre dbt, pero (según el README) de forma
  completa — falta la variante acotada por modelo/fuente para el endpoint
  de reprocesado puntual.

## Flow 1: validación + vinculación a fuente (extiende dataset_management.py, no 02_data_validation.py — ver nota al principio)

Debe considerar:
- Recibir `id_fuente` (si se proporcionó en el upload) además del
  `dataset_id` que ya maneja.
- Al llegar a `status='ready'`: ejecutar la lógica de `vigente` descrita en
  `fuentes_registradas_y_api.md` (marcar el dataset anterior de esa fuente
  como `vigente=FALSE`, actualizar `fuentes_registradas.id_dataset_actual`).
- Al llegar a `status='failed'`: no tocar `fuentes_registradas` ni el
  `vigente` de ningún otro dataset — solo registrar el fallo.
- Si no hay `id_fuente`: comportamiento actual, sin cambios (dataset
  huérfano).
- Idempotencia: si por algún motivo el flow se reintenta sobre el mismo
  dataset ya vinculado, no debe duplicar la actualización de vigencia ni
  crear inconsistencias (comprobar el estado actual antes de escribir).

## Flow 2: carga a `staging.*` (sustituye/generaliza 04_staging_manual.py)

Esto es el hueco más grande señalado en el propio README ("la ingesta
automatizada todavía no está implementada"). Debe considerar:

- **Un dispatcher por `codigo_fuente`**, no un único parser genérico: cada
  una de las 12 fuentes tiene estructura distinta (columnas, formato de
  `Municipios`, presencia o no de `Distritos`/`Secciones`/`Sexo`, formato
  de tabla ancha vs. larga en el caso de transacciones) — ver el detalle
  completo, ya cerrado, en `especificacion_carga_datos_TFM.md`. El flow debe
  leer `fuentes_registradas.codigo_fuente` para decidir qué función de
  parseo/limpieza aplicar.
- **Reglas de limpieza transversales a aplicar siempre** (ya acordadas):
  filtro de municipio case-sensitive con `trim()`, conversión numérica
  estándar español (miles con `.`, decimal con `,`) excepto en Tinsa (ya
  viene en formato estándar), filtro `Secciones` vacío cuando exista esa
  columna.
- **Caso especial transacciones (Ministerio)**: no es una simple limpieza de
  filas — requiere el algoritmo de recorrido secuencial fila-por-fila para
  distinguir cabecera de provincia vs. fila de municipio, y "propagar" el
  año de la celda combinada a sus 4 columnas de trimestre antes de pivotar
  a formato largo. Es la lógica más compleja de las 12 fuentes; conviene
  aislarla en su propia función/tarea, testeada de forma independiente.
- **Caso especial Tinsa**: resolver `id_geografia` por profundidad de URL +
  join contra `seed_geografia_tinsa`, nunca por texto de `zona` (ver
  especificación). No aplica la conversión de coma española.
- El flow debe leer el archivo desde MinIO usando la `storage_key` del
  dataset **vigente** de la fuente (join `fuentes_registradas` →
  `datasets_upload` filtrando `vigente=TRUE`), no simplemente "el último
  subido" — para que un archivo huérfano o uno fallido nunca se cargue por
  error.
- Al terminar de escribir en `staging.*`: registrar de algún modo que esa
  fuente ya se procesó hasta esta versión (por ejemplo, actualizando
  `fuentes_registradas.fecha_ultima_actualizacion` de nuevo, o un campo
  adicional tipo `fecha_ultima_carga_staging` si se quiere distinguir "se
  vinculó el archivo" de "se cargó efectivamente a staging").

## Flow 3: dbt run acotado (extiende 03_dbt_run.py)

Debe considerar:
- Aceptar un parámetro opcional de selector dbt (nombre de modelo o lista),
  para poder ejecutar `dbt run --select <stg_modelo_destino>+` en vez de
  `dbt run` completo — el `+` incluye automáticamente los modelos
  intermedios/core/marts que dependen aguas abajo.
- Si no se recibe selector, mantener el comportamiento actual (`dbt run`
  completo) — para las cargas iniciales o reconstrucciones totales.
- Este flow es el que dispararía el endpoint opcional
  `POST /fuentes_registradas/{id_fuente}/reprocesar` mencionado en
  `fuentes_registradas_y_api.md`, pasándole
  `fuentes_registradas.stg_modelo_destino` como selector. Nota: para la
  fuente Tinsa, `stg_modelo_destino` es un único modelo ahora
  (`stg_precios_tinsa`), así que el selector es directo; no hace falta
  lógica especial para múltiples modelos por fuente en ningún caso actual.

## Orquestación end-to-end (orden de dependencias)

```
subida archivo (API)
    -> Flow 1: validar + vincular a fuente (marca vigente/histórico)
        -> [si status=ready] Flow 2: parsear y cargar a staging.<tabla>
            -> Flow 3: dbt run --select <stg_modelo_destino>+
```

Los 3 flows deben poder encadenarse automáticamente (subida exitosa dispara
la cadena completa) pero también ejecutarse de forma independiente/manual
para debugging (igual que hoy `04_staging_manual.py` se puede correr
suelto).

## Validación de calidad de datos (recordatorio, no es tarea de Prefect en sí)

Los tests de calidad ya definidos (rango por `tipo_indicador`, Hombres +
Mujeres = Población total-m, relationships de las FK en los hechos) viven
en `schema.yml` de dbt, no en Prefect — Prefect solo debe asegurarse de que
`dbt test` se ejecute como parte del Flow 3 (o inmediatamente después) y de
que un fallo de test se refleje de forma visible (log, estado del flow en
Prefect UI), no solo un `dbt run` sin verificación posterior.
