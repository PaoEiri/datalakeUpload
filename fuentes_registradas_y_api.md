# Catálogo de fuentes registradas + actualización de archivos existentes

Complementa el README actual del proyecto. Resuelve dos huecos: (1) los 3
seeds curados a mano no deben tratarse como `dbt seed` recurrente, y (2) no
existe forma de saber que un archivo recién subido es la actualización de
una fuente ya conocida (ej. una nueva versión de `69303.csv`).

---

## 1. Los 3 seeds pasan a esquema `reference`, carga única

`dim_geografia`, `seed_indicadores_fuentes`, `seed_geografia_tinsa` **no se
declaran como `dbt seed` recurrente** — un `dbt seed` hace full-refresh desde
el CSV en cada ejecución y borraría silenciosamente cualquier edición manual
hecha directamente en Postgres.

**Tratamiento:**
1. Carga inicial única (una sola vez, vía script de migración o `dbt seed`
   ejecutado manualmente la primera vez) hacia un esquema nuevo `reference`.
2. A partir de ahí son tablas Postgres normales, editables directamente.
3. Los modelos `core/dim_geografia.sql`, etc. pasan a ser un simple
   pass-through:
   ```sql
   -- models/core/dim_geografia.sql
   select * from {{ source('reference', 'dim_geografia') }}
   ```
4. Añadir en `staging/sources.yml` (o un `sources.yml` propio para
   `reference`):
   ```yaml
   sources:
     - name: reference
       schema: reference
       tables:
         - name: dim_geografia
         - name: seed_indicadores_fuentes
         - name: seed_geografia_tinsa
   ```

---

## 2. Tabla `public.fuentes_registradas`

Catálogo estable de "qué fuentes lógicas existen", independiente de cuántas
veces se haya subido un archivo para cada una. Vive junto a
`datasets_upload`, no lo sustituye — `datasets_upload` sigue guardando cada
subida como fila inmutable (historial completo); `fuentes_registradas` solo
apunta a cuál es la vigente.

```sql
CREATE TABLE public.fuentes_registradas (
    id_fuente                  SERIAL PRIMARY KEY,
    sistema_origen              VARCHAR(20) NOT NULL
        CHECK (sistema_origen IN ('INE', 'Tinsa', 'Ministerio')),
    codigo_fuente                VARCHAR(50) NOT NULL UNIQUE,
        -- ej. '69303', 'tinsa_precios', 'transacciones_libre'
    nivel_territorial            VARCHAR(20) NOT NULL
        CHECK (nivel_territorial IN ('Municipio', 'Distrito', 'Ambos', 'Multiescala')),
    stg_modelo_destino           VARCHAR(200) NOT NULL,
        -- nombre del/los modelo(s) stg_*.sql que procesan esta fuente
    id_dataset_actual            INT REFERENCES public.datasets_upload(id),
        -- apunta a la fila vigente en datasets_upload; NULL si nunca se ha cargado
    fecha_ultima_actualizacion   TIMESTAMP,
    creado_en                    TIMESTAMP DEFAULT now()
);
```

### Cambio estructural: Tinsa pasa a un único archivo y un único modelo

El diseño anterior (`stg_precios_vivienda.sql` + `stg_precios_andalucia_espana.sql`,
dos modelos) corresponde a cuando las fuentes estaban separadas por nivel
territorial. Ya no aplica: el archivo `tinsa_malaga_andalucia.csv` está
unificado y resuelve país/CCAA/provincia/municipio/distrito por profundidad
de URL (vía `seed_geografia_tinsa`, ya diseñado). **Acción sobre el proyecto
real**: consolidar ambos modelos en uno solo, `stg_precios_tinsa.sql`, y
eliminar los dos anteriores.

### Auditoría: `public.fuentes_registradas_historial`

`fuentes_registradas.fecha_ultima_actualizacion` solo indica *cuándo* fue el
último cambio, no deja ver el historial completo de qué dataset reemplazó a
cuál. Se añade una tabla de auditoría mínima, dedicada solo a registrar cada
cambio de vigencia:

```sql
CREATE TABLE public.fuentes_registradas_historial (
    id_historial            SERIAL PRIMARY KEY,
    id_fuente                INT NOT NULL REFERENCES public.fuentes_registradas(id_fuente),
    id_dataset_anterior      INT REFERENCES public.datasets_upload(id),
        -- NULL en la primera carga de una fuente (no había versión previa)
    id_dataset_nuevo         INT NOT NULL REFERENCES public.datasets_upload(id),
    fecha_cambio             TIMESTAMP NOT NULL DEFAULT now()
);
```

Con esto, `SELECT * FROM fuentes_registradas_historial WHERE id_fuente = X
ORDER BY fecha_cambio` da la línea de tiempo completa de una fuente: qué
archivo estuvo vigente en cada periodo, sin tener que reconstruirlo a partir
de `created_at`/`vigente` en `datasets_upload`.

```sql
INSERT INTO public.fuentes_registradas
    (sistema_origen, codigo_fuente, nivel_territorial, stg_modelo_destino)
VALUES
    ('INE', '31106', 'Ambos',     'stg_renta_media'),
    ('INE', '31107', 'Ambos',     'stg_fuentes_ingreso'),
    ('INE', '37706', 'Ambos',     'stg_gini_p20_distritos'),
    ('INE', '2882',  'Municipio', 'stg_poblacion_sexo'),
    ('INE', '69303', 'Municipio', 'stg_indicadores_malaga'),
    ('INE', '69307', 'Municipio', 'stg_indicadores_turismo'),
    ('INE', '31114', 'Ambos',     'stg_indicadores_malaga_distrito'),
    ('INE', '69301', 'Municipio', 'stg_indicadores_ine'),
        -- el nombre exacto del modelo stg_* que procesa cada código INE es
        -- secundario: la deduplicación entre archivos que comparten
        -- indicador (mismo nombre, distinto nivel) ya la resuelve
        -- seed_indicadores_fuentes vía concepto_id / aplica_municipal /
        -- aplica_distrital, no depende de acertar el mapeo aquí

    ('Tinsa', 'tinsa_precios', 'Multiescala', 'stg_precios_tinsa'),
        -- un único archivo, un único modelo (ver nota arriba)

    ('Ministerio', 'transacciones_libre',       'Municipio', 'stg_transacciones_libre'),
    ('Ministerio', 'transacciones_segunda_mano','Municipio', 'stg_transacciones_segunda_mano'),
    ('Ministerio', 'transacciones_nueva',       'Municipio', 'stg_transacciones_nueva'),
    ('Ministerio', 'transacciones_protegida',   'Municipio', 'stg_transacciones_protegida');
```

---

## 3. Ajuste de la API — parámetro `id_fuente` en la subida (Opción A: vínculo explícito)

### `POST /datasets_upload/upload`

Añadir parámetro **opcional**:

```
POST /datasets_upload/upload
Form-data:
    file: <archivo>
    id_fuente: <int, opcional>   # FK a fuentes_registradas.id_fuente
```

**Cambio adicional en `public.datasets_upload`**: añadir columna
`vigente BOOLEAN NOT NULL DEFAULT TRUE`. Se mantiene separada de `status`
a propósito: `status` sigue describiendo únicamente el resultado de la
validación técnica del archivo (`pending/validating/ready/failed`);
`vigente` describe si ese archivo es la versión activa de su fuente dentro
del pipeline. Mezclar ambos conceptos en un solo campo generaría estados
ambiguos (un archivo puede ser `status='ready'` — técnicamente válido — y
aun así estar `vigente=FALSE` porque una versión más reciente lo sustituyó).

**Lógica en `datasets.py`:**

1. El flujo actual de subida (validar, guardar en MinIO, registrar en
   `datasets_upload`, disparar validación en Prefect) **no cambia**.
2. Si se recibe `id_fuente`:
   - Al finalizar la validación con éxito (`status = 'ready'`):
     ```sql
     -- 1) el dataset previamente vigente de esta fuente pasa a histórico
     UPDATE public.datasets_upload
     SET vigente = FALSE
     WHERE id = (SELECT id_dataset_actual FROM public.fuentes_registradas
                 WHERE id_fuente = :id_fuente);

     -- 2) registrar el cambio en la auditoría (antes de sobrescribir
     --    id_dataset_actual, para poder capturar el valor "anterior")
     INSERT INTO public.fuentes_registradas_historial
         (id_fuente, id_dataset_anterior, id_dataset_nuevo)
     SELECT id_fuente, id_dataset_actual, :nuevo_dataset_id
     FROM public.fuentes_registradas
     WHERE id_fuente = :id_fuente;

     -- 3) el catálogo apunta al nuevo dataset
     UPDATE public.fuentes_registradas
     SET id_dataset_actual = :nuevo_dataset_id,
         fecha_ultima_actualizacion = now()
     WHERE id_fuente = :id_fuente;
     ```
   - Si la validación falla (`status = 'failed'`), **no** se toca
     `fuentes_registradas`, `fuentes_registradas_historial` ni `vigente` de
     nada — la fuente sigue apuntando a la última versión válida conocida,
     y el archivo fallido queda registrado en `datasets_upload` con
     `status='failed'`, `vigente=FALSE` (nunca llegó a ser la versión
     activa, así que no genera entrada de auditoría).
3. Si **no** se recibe `id_fuente`: el dataset se registra igual en
   `datasets_upload` (con `vigente=TRUE` por defecto, ya que no compite con
   ninguna otra versión), pero queda "huérfano" (no vinculado a ninguna
   fuente catalogada) — útil para exploración de datasets nuevos antes de
   formalizarlos.
4. Con esto, `datasets_upload` conserva el historial completo de todas las
   versiones de cada fuente (auditoría/reproducibilidad académica), una
   consulta simple (`WHERE vigente = TRUE`) siempre da la versión activa, y
   `fuentes_registradas_historial` da la línea de tiempo explícita de qué
   dataset reemplazó a cuál y cuándo, sin tener que reconstruirla.

### Nuevo endpoint: `GET /fuentes_registradas`

Lista el catálogo con el dataset vigente de cada fuente (join contra
`datasets_upload` para traer `original_filename`, `row_count`,
`updated_at`, etc.). Útil para una pantalla de administración simple, o
para que Prefect consulte qué reprocesar.

### Nuevo endpoint (opcional): `POST /fuentes_registradas/{id_fuente}/reprocesar`

Dispara el flujo de Prefect (`flows/03_dbt_run.py`) acotado solo al/los
modelo(s) de `stg_modelo_destino` de esa fuente y sus dependientes aguas
abajo (selector dbt `--select stg_modelo_destino+`). Evita tener que
re-ejecutar `dbt run` completo cada vez que se actualiza un único archivo.

---

## Pendiente antes de implementar

Confirmar los 2 mapeos marcados `_CONFIRMAR` en el INSERT — sin eso, esas 2
filas quedarían con un `codigo_fuente` inválido/temporal en el catálogo.
