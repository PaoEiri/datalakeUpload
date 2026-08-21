from fastapi import APIRouter, Depends
from sqlalchemy import text

from src.db.database import SessionLocal

from .schemas import PrediccionesListResponse, PrediccionRow

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=PrediccionesListResponse)
async def list_predicciones(db=Depends(get_db)) -> PrediccionesListResponse:
    """Solo lectura: consulta fact_predicciones ya materializada por el flow
    de ML (flows/05_ml_train.py). No se hace inferencia en vivo aquí."""
    query = """
        SELECT
            dg.nombre AS nombre_geografia,
            dt.anio,
            dt.trimestre,
            fp.precio_predicho,
            fp.intervalo_inferior,
            fp.intervalo_superior,
            fp.es_forecast,
            dm.version AS version_modelo,
            dm.nombre_modelo AS algoritmo
        FROM marts.fact_predicciones fp
        JOIN core.dim_modelo dm ON fp.id_modelo = dm.id_modelo
        JOIN core.dim_geografia dg ON fp.id_geografia = dg.id_geografia
        JOIN core.dim_tiempo dt ON fp.id_tiempo = dt.id_tiempo
        WHERE dm.es_champion = true
        ORDER BY dt.anio, dt.trimestre
    """
    rows = db.execute(text(query)).mappings().all()
    return PrediccionesListResponse(predicciones=[PrediccionRow(**r) for r in rows])
