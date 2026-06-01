## Plan: Integrar subida y catálogo de datasets_upload con FastAPI + Prefect

TL;DR - Añadir un microservicio FastAPI para recibir CSV/JSON, guardar los bytes en MinIO y materializar metadatos en PostgreSQL. La validación y extracción de metadatos se hará de forma asíncrona con Prefect, mientras el catálogo y la previsualización se exponen como APIs REST.

**Pasos**
1. Crear una API REST nueva en `src/api`.
   - `src/api/app.py` con la instancia de FastAPI.
   - `src/api/datasets.py` con routers para subir archivos, listar datasets, obtener metadata y preview.
   - `src/api/schemas.py` con los modelos Pydantic de request/response.
2. Añadir la capa de almacenamiento sobre MinIO en `src/storage`.
   - `src/storage/minio_client.py` o `src/storage/object_store.py` con cliente `boto3` usando `endpoint_url`, credenciales y bucket.
   - métodos para subir bytes, descargar primeros bytes / objeto parcial, y verificar existencia.
3. Añadir la capa de base de datos en `src/db`.
   - `src/db/database.py` con engine `SQLAlchemy` async + `asyncpg`.
   - `src/db/models.py` con tabla `Dataset` para metadata y estado.
   - `src/db/crud.py` para crear registros, resolver nombres duplicados, actualizar estado y leer catálogo.
4. Diseñar el modelo de datos de metadatos.
   - campos básicos: `id`, `dataset_name`, `original_name`, `storage_key`, `format`, `content_type`, `size_bytes`, `status`, `error_message`, `created_at`, `updated_at`.
   - metadatos enriquecidos: `row_count`, `column_count`, `schema_json` con columnas y tipos, `preview_json` con primeras filas.
   - `status` para controlar flujo: `pending`, `validating`, `ready`, `failed`.
5. Crear la lógica de resolución de nombres duplicados.
   - función que consulta nombres existentes y genera `fichero.csv`, `fichero (1).csv`, `fichero (2).csv`, etc.
   - usarlo antes de subir el archivo para garantizar nombre único.
6. Añadir flujo Prefect para validación y metadatos en `flows/dataset_management.py`.
   - `@flow` que recibe `dataset_id`, `bucket_name`, `object_key`.
   - tareas: validar formato CSV/JSON, contar filas, detectar columnas, extraer tipos, generar preview y actualizar Postgres.
   - registrar cambios de estado en metadata: `validating`, `ready`, `failed`.
7. Conectar la API con Prefect.
   - en `POST /datasets_upload/upload`, tras subir el objeto y crear el registro DB, lanzar el flujo Prefect de forma asíncrona.
   - si se usa Prefect Server, `prefect.client.orchestration.get_client` o `prefect.client` para ejecutar el flow.
8. Actualizar infraestructura de Docker.
   - crear `infra/Dockerfile.api` para la nueva API con `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `python-multipart` y dependencias existentes.
   - añadir servicio `dataset-api` en `infra/docker-compose.yml` con puertos, dependencias a `postgres` y `minio`, y env vars para PostgreSQL y MinIO.
   - añadir variable `DATASETS_BUCKET` y crear bucket en `infra/init-minio.sh`.
9. Revisar y ampliar el despliegue Prefect.
   - extender `flows/deploy.py` para registrar `dataset_management_flow` o agregar un deployment opcional.
   - asegurar que el worker de Prefect puede ejecutar el nuevo flujo; si es necesario, construir una imagen `infra/Dockerfile.worker` con las nuevas dependencias sobre el agente actual.
10. Actualizar dependencias.
   - `requirements.txt` / `pyproject.toml` con `fastapi`, `uvicorn[standard]`, `python-multipart`, `sqlalchemy`, `asyncpg`.
   - mantener `boto3`, `pandas`, `prefect` y demás librerías ya presentes.
11. Documentar el uso.
   - añadir sección al `README.md` explicando los endpoints de dataset y el flujo asíncrono.
   - incluir comandos de Docker Compose para levantar la API y probar uploads.

**Verificación**
1. Levantar `docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml up -d`.
2. Probar `POST /datasets_upload/upload` con un CSV y un JSON válido.
3. Confirmar que el objeto se guarda en MinIO en el bucket `DATASETS_BUCKET` y que el registro inicial queda en PostgreSQL con `status=pending`.
4. Verificar que el flujo Prefect actualiza el registro a `ready` y rellena `row_count`, `column_count`, `schema_json` y `preview_json`.
5. Probar `GET /datasets_upload`, `GET /datasets_upload/{id}` y `GET /datasets_upload/{id}/preview`.
6. Subir el mismo fichero varias veces y verificar que los nombres terminan en `(1)`, `(2)`, etc.
7. Comprobar que la previsualización no requiere descargar el dataset completo y que funciona para archivos grandes con la muestra caché.

**Decisiones clave**
- No hay una API FastAPI existente en el repositorio, por lo que se debe crear un servicio nuevo.
- MinIO queda como almacenamiento de bytes; PostgreSQL queda como metadatos y catálogo.
- El pipeline de metadata/validación se implementa con Prefect para cumplir la exigencia de procesamiento asíncrono.
- Se reutiliza `boto3`, `pandas` y `prefect` ya presentes; se agregan solo las librerías estrictamente necesarias para FastAPI y acceso a Postgres.

**Archivos principales a modificar / crear**
- `src/api/app.py`
- `src/api/datasets.py`
- `src/api/schemas.py`
- `src/db/database.py`
- `src/db/models.py`
- `src/db/crud.py`
- `src/storage/minio_client.py`
- `flows/dataset_management.py`
- `flows/deploy.py`
- `infra/Dockerfile.api`
- `infra/docker-compose.yml`
- `infra/init-minio.sh`
- `requirements.txt` / `pyproject.toml`
- `README.md`
