# Diseño e Implementación de un Data Warehouse para el Análisis del Mercado Inmobiliario en España

Trabajo Final de Máster — Arquitectura de datos end-to-end para la ingesta, almacenamiento, transformación y visualización de datos abiertos del mercado inmobiliario español.

---

## Descripción general

El proyecto implementa un pipeline de datos completo que parte de ficheros de datos abiertos (CSV/JSON) publicados por organismos como el INE y los transforma en un modelo dimensional (esquema estrella) listo para su explotación analítica en Power BI.

La arquitectura separa claramente las responsabilidades en capas:

- **Ingesta**: API REST que acepta ficheros y los almacena en un object storage
- **Catálogo**: base de datos de metadatos independiente del almacenamiento de bytes
- **Orquestación**: flujos asíncronos que validan, extraen metadatos y transforman los datos
- **Data Warehouse**: modelo dimensional en tres capas (staging → core → marts)
- **Visualización**: conexión directa desde Power BI a la capa marts

---

## Arquitectura

```
CSV / JSON
    │
    ▼
FastAPI (dataset-api)
    ├── Valida formato y contenido
    ├── Almacena bytes en MinIO (object storage)
    ├── Registra metadatos en PostgreSQL (public.datasets_upload)
    └── Dispara flujo asíncrono en Prefect
            │
            ▼
        Prefect Worker
            ├── Extrae metadatos: columnas, tipos, filas, tamaño
            ├── Actualiza estado en catálogo (pending → validating → ready)
            └── Carga datos limpios en staging (pandas)
                    │
                    ▼
                dbt
                    ├── staging.stg_ipv           (view)
                    ├── core.dim_comunidad         (table)
                    ├── core.dim_tiempo            (table)
                    ├── core.dim_indicador         (table)
                    ├── core.dim_tipo_vivienda     (table)
                    └── marts.fct_precios_vivienda (table)
                                │
                                ▼
                            Power BI
```

---

## Stack tecnológico

| Componente | Tecnología | Rol |
|---|---|---|
| API REST | FastAPI + Python | Ingesta de ficheros |
| Object storage | MinIO (S3-compatible) | Almacenamiento de bytes |
| Base de datos | PostgreSQL 16 | Metadatos + Data Warehouse |
| Orquestación | Prefect 3 | Flujos asíncronos |
| Transformación | pandas | Limpieza y carga a staging |
| Modelado | dbt (dbt-postgres) | Capas core y marts |
| Visualización | Power BI Desktop | Dashboards analíticos |
| Contenedores | Docker + Docker Compose | Infraestructura local |

---

## Estructura del proyecto

```
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── models/
│       ├── staging/
│       │   ├── sources.yml
│       │   └── stg_ipv.sql
│       ├── core/
│       │   ├── dim_geografia.sql
│       │   ├── dim_tiempo.sql
│       │   ├── dim_indicador.sql
│       │   └── dim_tipo_vivienda.sql
│       └── marts/
│           ├── schema.yml
│           └── fact_precios_vivienda.sql
├── flows/
│   
│   ├── 01_data_validation.py
│   ├── 02_dbt_run.py
│   ├── 03_staging_manual.py
│   └── dataset_management.py
├── infra/
│   ├── docker-compose.yml
│   ├── docker-compose.prefect.yml
│   ├── docker-compose.dbt.yml
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.dbt
│   ├── init-minio.sh
│   └── docker-entrypoint-initdb.d/
│       ├── 01_init.sql
│       ├── 02_dw_schemas.sql
│       └── 03_staging.sql
└── src/
    ├── api/
    │   ├── app.py
    │   ├── datasets.py
    │   └── schemas.py
    ├── db/
    │   ├── database.py
    │   ├── crud_sync.py
    │   └── models.py
    ├── storage/
    ├── tasks/
    │   ├── dbt.py
    │   └── staging.py
    └── config.py
```

---

## Esquema de base de datos

### Esquema `public` — catálogo de datasets

```sql
public.datasets_upload
    id               SERIAL PRIMARY KEY
    dataset_name     VARCHAR(255) UNIQUE   -- nombre único generado automáticamente
    original_filename VARCHAR(255)         -- nombre original del fichero subido
    storage_key      VARCHAR(512)          -- clave en MinIO
    file_format      VARCHAR(50)           -- csv | json
    content_type     VARCHAR(100)
    size_bytes       BIGINT
    row_count        INTEGER               -- extraído automáticamente
    column_count     INTEGER               -- extraído automáticamente
    schema           JSONB                 -- columnas y tipos de datos
    preview          JSONB                 -- primeras 20 filas
    status           VARCHAR(50)           -- pending | validating | ready | failed
    error_message    TEXT
    created_at       TIMESTAMP
    updated_at       TIMESTAMP
```

### Esquema `staging` — datos crudos limpios

```sql
staging.ipv_precios_vivienda
    tipo_vivienda    VARCHAR(50)
    ambito           VARCHAR(50)
    comunidad        VARCHAR(100)
    indicador        VARCHAR(100)
    anio             SMALLINT
    trimestre        SMALLINT
    fecha            DATE                  -- primer día del trimestre
    valor            NUMERIC(12,4)
    fuente           VARCHAR(200)
    cargado_en       TIMESTAMP
```

### Esquema `core` — dimensiones

```
dim_comunidad       -- 20 comunidades autónomas + Nacional con código INE
dim_tiempo          -- 76 periodos trimestrales con label legible
dim_indicador       -- tipos de índice y variación
dim_tipo_vivienda   -- general, vivienda nueva, segunda mano
```

### Esquema `marts` — tabla de hechos

```
fct_precios_vivienda  -- 18.240 filas, joins con las 4 dimensiones
```

---

## Capacidades de la API

- `POST /datasets_upload/upload` — subir CSV o JSON, almacenar en MinIO y programar validación asíncrona.
- `GET /datasets_upload` — listar todos los datasets uploads disponibles y metadatos básicos.
- `GET /datasets_upload/{dataset_id}` — obtener información detallada de un dataset upload.
- `GET /datasets_upload/{dataset_id}/preview` — ver las primeras filas extraídas sin descargar el dataset 

---

## Separación de responsabilidades

El sistema mantiene dos sistemas de almacenamiento con responsabilidades distintas:

**MinIO** almacena los bytes del fichero original sin modificación. Es el data lake raw. Un fichero de 50 MB se guarda tal cual, sin procesamiento.

**PostgreSQL** almacena la información *sobre* los ficheros: cuántas filas tienen, qué columnas, cuándo se subieron, si son válidos. No guarda los datos en sí.

Esta separación permite consultar el catálogo (qué datasets existen, qué columnas tienen) sin leer ningún fichero, y permite regenerar las transformaciones del DW en cualquier momento relanzando los flujos de Prefect y dbt.

---

## Puesta en marcha

### Requisitos

- Docker Desktop
- Docker Compose
- Power BI Desktop (Windows)

### Variables de entorno

Copia `.env.example` a `.env` y rellena los valores:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=datalake
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ENDPOINT=http://minio:9000
MINIO_SECURE=false
DATASETS_BUCKET=datasets-upload

PREFECT_API_HOST=prefect-server
PREFECT_API_PORT=4200
DATASET_API_PORT=8000

DBT_PROJECT_DIR=/app/dbt
DBT_PROFILES_DIR=/app/dbt
DBT_TARGET=dev
```

### Levantar el stack

```bash
# Stack principal (API + MinIO + PostgreSQL)
docker compose -f infra/docker-compose.yml up -d

# Stack de orquestación (Prefect)
docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml up -d

# Stack completo incluyendo dbt docs
docker compose \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.prefect.yml \
  -f infra/docker-compose.dbt.yml \
  --profile dbt up -d
```

### Crear esquemas del Data Warehouse (primera vez)

```bash
docker exec -it postgres psql -U $POSTGRES_USER -d $POSTGRES_DB \
  -c "CREATE SCHEMA IF NOT EXISTS staging;
      CREATE SCHEMA IF NOT EXISTS core;
      CREATE SCHEMA IF NOT EXISTS marts;"
```

### Ejecutar transformaciones dbt

```bash
# Desde el contenedor dbt
docker exec -it dbt dbt run

# Desde el worker de Prefect
docker exec -it prefect-worker python flows/03_dbt_run.py
```

---

## Interfaces web

| Servicio | URL |
|---|---|
| API REST (docs) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |
| Prefect UI | http://localhost:4200 |
| dbt docs | http://localhost:8080 |

---

## Dataset de prueba

**INE — Índice de Precios de Vivienda (IPV)**

Fuente: Instituto Nacional de Estadística  
Formato: CSV con separador `;` y codificación `latin-1`  
Cobertura: series trimestrales desde 2007 por comunidad autónoma  
Indicadores: índice base, variación trimestral, variación anual, variación acumulada  
Filas cargadas: 18.240

El pipeline completo para este dataset va de la subida del CSV a través de la API hasta la tabla `marts.fct_precios_vivienda` lista para conectar en Power BI, pasando por validación automática, extracción de metadatos, limpieza con pandas y modelado dimensional con dbt.

# Para ejecutar actualizado 
docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml -f infra\docker-compose.dbt.yml build

docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml -f infra/docker-compose.dbt.yml --profile dbt up -d

docker exec -it prefect-worker python flows/04_staging_manual.py 


docker exec -it prefect-worker python flows/03_dbt_run.py



