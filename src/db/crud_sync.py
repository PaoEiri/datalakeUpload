import os
from typing import Optional, Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Dataset, FuenteRegistrada, FuenteRegistradaHistorial, MLModelRegistry, PrediccionMLRaw


def resolve_dataset_name(db: Session, original_filename: str) -> str:
    base, ext = os.path.splitext(original_filename)
    candidate = original_filename
    index = 0

    while True:
        result = db.execute(select(Dataset).filter_by(dataset_name=candidate))
        if result.scalar_one_or_none() is None:
            return candidate
        index += 1
        candidate = f"{base} ({index}){ext}"


def create_dataset_record(
    db: Session,
    original_filename: str,
    storage_key: str,
    file_format: str,
    content_type: str,
    size_bytes: int,
    status: str = "pending",
    dataset_name: Optional[str] = None,
) -> Dataset:
    dataset_name = dataset_name or original_filename
    dataset_name = resolve_dataset_name(db, dataset_name)

    dataset = Dataset(
        dataset_name=dataset_name,
        original_filename=original_filename,
        storage_key=storage_key,
        file_format=file_format,
        content_type=content_type,
        size_bytes=size_bytes,
        status=status,
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def update_dataset_status(
    db: Session,
    dataset_id: int,
    status: str,
    row_count: Optional[int] = None,
    column_count: Optional[int] = None,
    schema: Optional[Sequence] = None,
    preview: Optional[Sequence] = None,
    error_message: Optional[str] = None,
) -> Dataset:
    result = db.execute(select(Dataset).filter_by(id=dataset_id))
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise ValueError(f"Dataset {dataset_id} not found")

    dataset.status = status
    if row_count is not None:
        dataset.row_count = row_count
    if column_count is not None:
        dataset.column_count = column_count
    if schema is not None:
        dataset.schema = schema
    if preview is not None:
        dataset.preview = preview
    if error_message is not None:
        dataset.error_message = error_message

    db.commit()
    db.refresh(dataset)
    return dataset


def set_dataset_vigente(db: Session, dataset_id: int, vigente: bool) -> Dataset:
    result = db.execute(select(Dataset).filter_by(id=dataset_id))
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise ValueError(f"Dataset {dataset_id} not found")
    dataset.vigente = vigente
    db.commit()
    db.refresh(dataset)
    return dataset


def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
    result = db.execute(select(Dataset).filter_by(id=dataset_id))
    return result.scalar_one_or_none()


def list_datasets(db: Session) -> list[Dataset]:
    result = db.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    return result.scalars().all()


# ---------------------------------------------------------
# fuentes_registradas
# ---------------------------------------------------------
def get_fuente(db: Session, id_fuente: int) -> Optional[FuenteRegistrada]:
    result = db.execute(select(FuenteRegistrada).filter_by(id_fuente=id_fuente))
    return result.scalar_one_or_none()


def get_fuente_by_codigo(db: Session, codigo_fuente: str) -> Optional[FuenteRegistrada]:
    result = db.execute(select(FuenteRegistrada).filter_by(codigo_fuente=codigo_fuente))
    return result.scalar_one_or_none()


def list_fuentes(db: Session) -> list[FuenteRegistrada]:
    result = db.execute(select(FuenteRegistrada).order_by(FuenteRegistrada.codigo_fuente))
    return result.scalars().all()


def marcar_dataset_vigente(db: Session, id_fuente: int, nuevo_dataset_id: int) -> FuenteRegistrada:
    """Aplica la transición de vigencia: el dataset anterior de la fuente pasa
    a histórico, se registra en la auditoría y fuentes_registradas apunta al
    nuevo dataset. Ver fuentes_registradas_y_api.md."""
    fuente = get_fuente(db, id_fuente)
    if fuente is None:
        raise ValueError(f"Fuente {id_fuente} no encontrada")

    if fuente.id_dataset_actual == nuevo_dataset_id:
        # Ya aplicado (reintento del flow sobre el mismo dataset) — no duplicar.
        return fuente

    dataset_anterior_id = fuente.id_dataset_actual

    if dataset_anterior_id is not None:
        anterior = get_dataset(db, dataset_anterior_id)
        if anterior is not None:
            anterior.vigente = False

    db.add(
        FuenteRegistradaHistorial(
            id_fuente=id_fuente,
            id_dataset_anterior=dataset_anterior_id,
            id_dataset_nuevo=nuevo_dataset_id,
        )
    )

    fuente.id_dataset_actual = nuevo_dataset_id
    import datetime

    fuente.fecha_ultima_actualizacion = datetime.datetime.utcnow()

    db.commit()
    db.refresh(fuente)
    return fuente


def get_vigente_dataset_por_fuente(db: Session, id_fuente: int) -> Optional[Dataset]:
    fuente = get_fuente(db, id_fuente)
    if fuente is None or fuente.id_dataset_actual is None:
        return None
    return get_dataset(db, fuente.id_dataset_actual)


# ---------------------------------------------------------
# ml_model_registry / fact_predicciones
# ---------------------------------------------------------
def create_model_registry_entry(
    db: Session,
    version: str,
    algoritmo: str,
    hiperparametros: Optional[dict],
    r2: float,
    accuracy_direccional: float,
    rmse: float,
    mae: float,
    ruta_minio_modelo: Optional[str] = None,
    ruta_minio_shap: Optional[str] = None,
    indicadores_usados: Optional[list] = None,
    importancia_features: Optional[list] = None,
) -> MLModelRegistry:
    modelo = MLModelRegistry(
        version=version,
        algoritmo=algoritmo,
        hiperparametros=hiperparametros,
        indicadores_usados=indicadores_usados,
        importancia_features=importancia_features,
        r2=r2,
        accuracy_direccional=accuracy_direccional,
        rmse=rmse,
        mae=mae,
        ruta_minio_modelo=ruta_minio_modelo,
        ruta_minio_shap=ruta_minio_shap,
    )
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    return modelo


def set_champion(db: Session, id_modelo: int) -> MLModelRegistry:
    """Marca id_modelo como el único champion activo (desmarca cualquier otro)."""
    db.query(MLModelRegistry).filter(MLModelRegistry.id_modelo != id_modelo).update(
        {"es_champion": False}
    )
    modelo = db.execute(select(MLModelRegistry).filter_by(id_modelo=id_modelo)).scalar_one_or_none()
    if modelo is None:
        raise ValueError(f"Modelo {id_modelo} no encontrado")
    modelo.es_champion = True
    db.commit()
    db.refresh(modelo)
    return modelo


def get_champion_model(db: Session) -> Optional[MLModelRegistry]:
    result = db.execute(select(MLModelRegistry).filter_by(es_champion=True))
    return result.scalar_one_or_none()


def create_prediccion(
    db: Session,
    id_geografia: int,
    anio: int,
    trimestre: int,
    id_modelo: int,
    precio_predicho: float,
    es_forecast: bool,
    intervalo_inferior: Optional[float] = None,
    intervalo_superior: Optional[float] = None,
) -> PrediccionMLRaw:
    prediccion = PrediccionMLRaw(
        id_geografia=id_geografia,
        anio=anio,
        trimestre=trimestre,
        id_modelo=id_modelo,
        precio_predicho=precio_predicho,
        intervalo_inferior=intervalo_inferior,
        intervalo_superior=intervalo_superior,
        es_forecast=es_forecast,
    )
    db.add(prediccion)
    db.commit()
    db.refresh(prediccion)
    return prediccion
