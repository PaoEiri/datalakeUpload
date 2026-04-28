# Módulo MLOps — MLflow + Prefect

Repositorio del módulo práctico de MLOps. Dos clases progresivas sobre el ciclo de vida de un modelo ML en producción, usando Docker como plataforma de despliegue.

---

## Estructura

```
modulo-mlops/
├── configs/
│   └── config.yaml          # Hiperparámetros, rutas, nombres de experimento
├── data/
│   └── raw/
│       └── telco_churn.csv  # Dataset Telco Customer Churn (7043 filas)
├── flows/                   # Clase 2 — flows de Prefect
│   ├── 01_hello_prefect.py      # Intro: @flow, @task, logging
│   ├── 02_data_validation.py    # Retries y observabilidad
│   ├── training_pipeline.py     # Pipeline completo (train → eval → register)
│   ├── retraining_trigger.py    # Schedule + sub-flows
│   ├── champion_promotion.py    # Promoción automática por AUC-ROC
│   └── deploy.py                # Registra work pool y deployments
├── infra/
│   ├── docker-compose.yml           # Stack Clase 1: PostgreSQL + MinIO + MLflow
│   ├── docker-compose.prefect.yml   # Stack Clase 2: Prefect server + worker
│   ├── Dockerfile.mlflow            # Imagen MLflow con dependencias S3
│   ├── Dockerfile.worker            # Imagen worker con paquetes ML pre-instalados
│   ├── .env                         # Variables de entorno (no commitear en prod)
│   └── init-minio.sh                # One-shot: crea bucket en MinIO
├── notebooks/
│   └── 01_eda.ipynb         # Exploración del dataset
└── src/
    ├── data_prep.py          # Carga y split del dataset
    ├── train.py              # Entrenamiento con MLflow autolog
    ├── evaluate.py           # mlflow.evaluate() + métricas y artifacts
    ├── register.py           # Model Registry: challenger/champion aliases
    └── predict.py            # Inferencia cargando @champion del registry
```

---

## Clase 1 — MLflow: tracking, evaluación y registry

**Stack:** PostgreSQL (backend) + MinIO (artifacts S3) + MLflow server

### Arrancar

```bash
cd infra
docker compose up -d
```

Esperar a que los 4 servicios estén healthy (~30 s). Verificar:
- MLflow UI: http://localhost:5001
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)

### Flujo de trabajo

```bash
# 1. Entrenar (xgboost, random_forest, logistic_regression)
uv run python src/train.py --config configs/config.yaml --model-type xgboost
uv run python src/train.py --config configs/config.yaml --model-type random_forest

# 2. Evaluar un run (copiar RUN_ID de la UI)
uv run python src/evaluate.py --run-id <RUN_ID>

# 3. Registrar como challenger y promover a champion
uv run python src/register.py --run-id <RUN_ID>
uv run python src/register.py --compare
uv run python src/register.py --promote-version <N>

# 4. Inferencia con el champion activo
uv run python src/predict.py --input data/raw/telco_churn.csv
```

---

## Clase 2 — Prefect: orquestación + integración con MLflow

**Stack:** todo lo anterior + Prefect server + Prefect worker (process pool)

### Arrancar el stack completo

```bash
cd infra

# Primera vez: construir imagen del worker (solo necesario una vez)
docker compose -f docker-compose.yml -f docker-compose.prefect.yml build

# Levantar todo
docker compose -f docker-compose.yml -f docker-compose.prefect.yml up -d
```

Servicios disponibles:
- Prefect UI: http://localhost:4200
- MLflow UI: http://localhost:5001
- MinIO Console: http://localhost:9001

### Registrar deployments (solo una vez tras levantar el stack)

```bash
PREFECT_API_URL=http://localhost:4200/api uv run python flows/deploy.py
```

### Ejecutar flows localmente

```bash
# Flow 1 — Intro: @task, @flow, logging
PREFECT_API_URL=http://localhost:4200/api uv run python flows/01_hello_prefect.py

# Flow 2 — Retries y observabilidad
PREFECT_API_URL=http://localhost:4200/api uv run python flows/02_data_validation.py

# Flow 3 — Pipeline completo: train → evaluate → register
PREFECT_API_URL=http://localhost:4200/api uv run python flows/training_pipeline.py

# Flow 4 — Sub-flows y schedules (usar max_age_days=0 para forzar retrain)
PREFECT_API_URL=http://localhost:4200/api uv run python -c "
import sys; sys.path.insert(0,'flows'); sys.path.insert(0,'src')
from retraining_trigger import retraining_trigger_flow
retraining_trigger_flow(max_age_days=0)
"

# Flow 5 — Promoción automática de champion
PREFECT_API_URL=http://localhost:4200/api uv run python flows/champion_promotion.py
```

Los deployments registrados también se pueden lanzar desde la UI en http://localhost:4200 → Deployments.

### Parar el stack

```bash
cd infra

# Parar sin borrar datos
docker compose -f docker-compose.yml -f docker-compose.prefect.yml down

# Parar y borrar volúmenes (reset completo)
docker compose -f docker-compose.yml -f docker-compose.prefect.yml down -v
```

---

## Requisitos

- Docker Desktop ≥ 4.x
- Python ≥ 3.11 (el stack usa Python 3.14 en el host, 3.11 en los workers Docker)
- [uv](https://docs.astral.sh/uv/) para gestión de entorno local

```bash
# Instalar dependencias locales
uv sync
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  Host (uv run python flows/...)                         │
│                                                         │
│  Prefect Client ──────────────────────────────────────► │
│                                    Prefect Server :4200 │
│  MLflow Client ───────────────────────────────────────► │
│                                    MLflow Server  :5001 │
└─────────────────────────────────────────────────────────┘
                        Docker network
┌─────────────────────────────────────────────────────────┐
│  prefect-server   :4200   ◄── prefect-worker            │
│  mlflow-server    :5001   ◄── prefect-worker (flows)    │
│  mlflow-postgres  :5432   ◄── mlflow-server             │
│                           ◄── prefect-server            │
│  mlflow-minio     :9000   ◄── mlflow-server (artifacts) │
└─────────────────────────────────────────────────────────┘
```

El worker Docker ejecuta los deployments cuando se lanzan desde la UI de Prefect. Los flows ejecutados localmente con `uv run` también aparecen en la UI de Prefect (si `PREFECT_API_URL` está seteado).
