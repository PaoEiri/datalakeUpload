from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from src.db.database import SessionLocal
from src.db import crud_sync

from .schemas import (
    FuenteRegistradaResponse,
    FuentesRegistradasListResponse,
    ReprocesarFuenteResponse,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def trigger_reprocesar_fuente(id_fuente: int) -> None:
    """Descarga de MinIO el dataset vigente de la fuente, lo carga a
    staging.<tabla> y ejecuta dbt run acotado a su modelo. Reutiliza el
    mismo flow que dispara la carga automática tras un upload."""
    from flows.dataset_management import cargar_staging_fuente
    from src.tasks.dbt import run_dbt
    from src.config import settings

    with SessionLocal() as db:
        fuente = crud_sync.get_fuente(db, id_fuente)
        dataset = crud_sync.get_vigente_dataset_por_fuente(db, id_fuente)

    if fuente is None or dataset is None:
        return

    stg_modelo_destino, _ = cargar_staging_fuente.fn(
        id_fuente, settings.datasets_bucket, dataset.storage_key
    )
    run_dbt.fn(select=f"{stg_modelo_destino}+")


@router.get("/", response_model=FuentesRegistradasListResponse)
async def list_fuentes_registradas(db=Depends(get_db)) -> FuentesRegistradasListResponse:
    fuentes = crud_sync.list_fuentes(db)
    resultado = []
    for fuente in fuentes:
        dataset_actual = None
        if fuente.id_dataset_actual is not None:
            dataset_actual = crud_sync.get_dataset(db, fuente.id_dataset_actual)
        resultado.append(
            FuenteRegistradaResponse.model_validate(
                {**fuente.__dict__, "dataset_actual": dataset_actual}
            )
        )
    return FuentesRegistradasListResponse(fuentes=resultado)


@router.post("/{id_fuente}/reprocesar", response_model=ReprocesarFuenteResponse)
async def reprocesar_fuente(
    id_fuente: int, background_tasks: BackgroundTasks, db=Depends(get_db)
) -> ReprocesarFuenteResponse:
    fuente = crud_sync.get_fuente(db, id_fuente)
    if fuente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuente no encontrada.")

    dataset = crud_sync.get_vigente_dataset_por_fuente(db, id_fuente)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La fuente todavía no tiene ningún dataset vigente cargado.",
        )

    background_tasks.add_task(trigger_reprocesar_fuente, id_fuente)

    return ReprocesarFuenteResponse(
        id_fuente=fuente.id_fuente,
        codigo_fuente=fuente.codigo_fuente,
        stg_modelo_destino=fuente.stg_modelo_destino,
        message="Reprocesado aceptado: carga a staging + dbt run acotado en curso.",
    )
