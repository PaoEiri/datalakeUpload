# Módulo MLOps — MLflow: Tracking, Evaluación y Model Registry

Este repositorio contiene una práctica completa de MLOps basada en un caso de uso real: predecir la fuga de clientes (churn) en una empresa de telecomunicaciones. El objetivo es aplicar el ciclo de vida completo de un modelo de machine learning, desde el entrenamiento hasta la inferencia en producción, usando herramientas modernas del ecosistema MLOps.

El proyecto está diseñado para ejecutarse de forma local con Docker, sin necesidad de Kubernetes ni infraestructura cloud. Todo el stack se levanta con un único comando y es fácilmente adaptable a un entorno de producción real.

## Tecnologías utilizadas

- MLflow 3.x – Seguimiento de experimentos, evaluación de modelos y registro con aliases
- PostgreSQL – Backend de metadatos para MLflow
- MinIO – Almacenamiento de artefactos compatible con S3
- Docker Compose – Orquestación local del stack completo
- scikit-learn / XGBoost – Modelos de clasificación
- uv – Gestión de entorno y dependencias Python

## Referencias recomendadas

- Whitepaper de Google sobre el ciclo de vida del ML:  
  https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf

Durante mi doctorado, escribí dos artículos directamente relacionados con la infraestructura utilizada en esta práctica:

- Artículo sobre la infraestructura MLOps que sirve de base para este repositorio:  
  https://ieeexplore.ieee.org/abstract/document/10588954/

- Artículo con un caso de uso completo en imágenes satélite, donde se automatiza el ciclo de vida de un modelo de ML:  
  https://www.sciencedirect.com/science/article/pii/S0167739X24004631

Recomiendo la lectura de ambos si te interesa profundizar en la aplicación práctica de MLOps.

## Estructura del repositorio

Cada carpeta representa una fase del ciclo de vida del modelo. El orden recomendado para explorar el proyecto es:

1. `infra/`  
   Stack de infraestructura completo: PostgreSQL como backend de metadatos, MinIO como almacén de artefactos compatible con S3, y el servidor MLflow conectando ambos. Se levanta con Docker Compose en un único comando.

2. `src/data_prep.py`  
   Carga y preprocesamiento del dataset: codificación de variables categóricas, split train/test y limpieza de valores nulos.

3. `src/api/app.py`, `src/api/datasets.py`
   Servicio FastAPI para subir datasets CSV/JSON, almacenar los bytes en MinIO, extraer metadatos en PostgreSQL y exponer un catálogo de datasets.

4. `src/train.py`
   Evaluación del modelo usando `mlflow.models.evaluate()`. Genera métricas de clasificación, curva ROC, matriz de confusión, curva precision-recall e importancia de features con SHAP, todo registrado como artefactos en MLflow.

5. `src/register.py`  
   Gestión del Model Registry con el patrón champion/challenger. Registra un modelo como `@challenger`, permite comparar sus métricas frente al `@champion` actual y promoverlo si lo supera.

6. `src/predict.py`  
   Inferencia cargando siempre el modelo con el alias `@champion` desde el registry. Sin hardcodear versiones — el alias apunta automáticamente al modelo en producción.

7. `notebooks/01_eda.ipynb`  
   Exploración inicial del dataset: distribuciones, correlaciones y análisis de la variable objetivo.

## Dataset

- Dataset Telco Customer Churn disponible en Kaggle:  
  https://www.kaggle.com/datasets/blastchar/telco-customer-churn

El dataset contiene 7043 registros de clientes con características como tipo de contrato, servicios contratados y cargo mensual. La variable objetivo indica si el cliente canceló el servicio. Se utiliza sin reducción ya que su tamaño es manejable para ejecución local.

## Recursos de aprendizaje recomendados

- Curso introductorio de Andrew Ng sobre ML en producción (Coursera, 10 horas):  
  https://www.coursera.org/learn/introduction-to-machine-learning-in-production

- Especialización en MLOps de Duke University (Coursera):  
  https://www.coursera.org/specializations/mlops-machine-learning-duke

- Curso de MLOps en Google Cloud (Coursera):  
  https://www.coursera.org/learn/gcp-production-ml-systems

## Objetivo

Este repositorio tiene un enfoque educativo y práctico, ideal para personas que quieran entender cómo se gestiona el ciclo de vida de un modelo de machine learning con herramientas reales. Cada componente está desacoplado y puede ejecutarse de forma independiente, lo que facilita la comprensión de cada etapa del proceso sin necesidad de infraestructura compleja.


## Comandos prefect

cd infra && docker compose -f docker-compose.yml -f docker-compose.prefect.yml build
docker compose -f docker-compose.yml -f docker-compose.prefect.yml up -d


 docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml build

 docker compose -f infra/docker-compose.yml -f infra/docker-compose.prefect.yml up -d
## API de datasets_upload

Una vez levantado el stack, el servicio de datasets_upload está disponible en `http://localhost:8000`.

- `POST /datasets_upload/upload` — subir CSV o JSON, almacenar en MinIO y programar validación asíncrona.
- `GET /datasets_upload` — listar todos los datasets uploads disponibles y metadatos básicos.
- `GET /datasets_upload/{dataset_id}` — obtener información detallada de un dataset upload.
- `GET /datasets_upload/{dataset_id}/preview` — ver las primeras filas extraídas sin descargar el dataset completo.
