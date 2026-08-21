from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import text

from src.db.database import SessionLocal

from .schemas import (
    AplicarCambiosResponse,
    EditarIndicadorRequest,
    EditarIndicadorResponse,
    IndicadorReferenciaRow,
    IndicadoresReferenciaListResponse,
    ToggleIndicadorRequest,
    ToggleIndicadorResponse,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def trigger_dbt_run() -> None:
    from src.tasks.dbt import run_dbt

    run_dbt.fn(select="int_indicadores_unificado+")


@router.get("/", response_model=IndicadoresReferenciaListResponse)
async def list_indicadores_referencia(db=Depends(get_db)) -> IndicadoresReferenciaListResponse:
    query = """
        SELECT
            s.indicador_id,
            s.nombre_indicador,
            s.categoria_indicador,
            s.descripcion,
            s.aplica_municipal,
            s.aplica_distrital,
            s.usar_en_ml,
            cm.cobertura_pct AS cobertura_municipal_pct,
            cd.cobertura_pct AS cobertura_distrital_pct,
            s.notas_adaptacion
        FROM reference.seed_indicadores_fuentes s
        LEFT JOIN reporting.v_indicadores_cobertura cm
            ON cm.indicador_id = s.indicador_id AND cm.nivel_geografico = 'MUNICIPIO'
        LEFT JOIN reporting.v_indicadores_cobertura cd
            ON cd.indicador_id = s.indicador_id AND cd.nivel_geografico = 'DISTRITO'
        ORDER BY s.categoria_indicador, s.nombre_indicador
    """
    rows = db.execute(text(query)).mappings().all()
    return IndicadoresReferenciaListResponse(
        indicadores=[IndicadorReferenciaRow(**r) for r in rows]
    )


@router.patch("/{indicador_id}/toggle", response_model=ToggleIndicadorResponse)
async def toggle_indicador(
    indicador_id: int, body: ToggleIndicadorRequest, db=Depends(get_db)
) -> ToggleIndicadorResponse:
    columnas = {"municipal": "aplica_municipal", "distrital": "aplica_distrital", "ml": "usar_en_ml"}
    columna = columnas[body.nivel]
    db.execute(
        text(f"UPDATE reference.seed_indicadores_fuentes SET {columna} = :activo WHERE indicador_id = :id"),
        {"activo": body.activo, "id": indicador_id},
    )
    db.commit()
    return ToggleIndicadorResponse(indicador_id=indicador_id, nivel=body.nivel, activo=body.activo)


@router.patch("/{indicador_id}/editar", response_model=EditarIndicadorResponse)
async def editar_indicador(
    indicador_id: int, body: EditarIndicadorRequest, db=Depends(get_db)
) -> EditarIndicadorResponse:
    db.execute(
        text(
            "UPDATE reference.seed_indicadores_fuentes "
            "SET descripcion = :descripcion, notas_adaptacion = :notas "
            "WHERE indicador_id = :id"
        ),
        {"descripcion": body.descripcion, "notas": body.notas_adaptacion, "id": indicador_id},
    )
    db.commit()
    return EditarIndicadorResponse(
        indicador_id=indicador_id,
        descripcion=body.descripcion,
        notas_adaptacion=body.notas_adaptacion,
    )


@router.post("/aplicar_cambios", response_model=AplicarCambiosResponse)
async def aplicar_cambios(background_tasks: BackgroundTasks) -> AplicarCambiosResponse:
    background_tasks.add_task(trigger_dbt_run)
    return AplicarCambiosResponse(
        message="dbt run acotado (int_indicadores_unificado+) lanzado en background."
    )
