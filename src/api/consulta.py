from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from src.db.database import SessionLocal

from .schemas import (
    AniosListResponse,
    CategoriasIndicadorListResponse,
    GeografiaOption,
    GeografiasListResponse,
    IndicadorOption,
    IndicadoresListResponse,
    IndicadorValorListResponse,
    IndicadorValorRow,
    PrecioListResponse,
    PrecioRow,
)

router = APIRouter()


def get_db():
    """Dependencia síncrona para SQLAlchemy sync."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/geografias", response_model=GeografiasListResponse)
async def list_geografias(db=Depends(get_db)) -> GeografiasListResponse:
    rows = db.execute(
        text("SELECT id_geografia, nombre, nivel FROM core.dim_geografia ORDER BY nombre")
    ).mappings().all()
    return GeografiasListResponse(geografias=[GeografiaOption(**r) for r in rows])


@router.get("/anios", response_model=AniosListResponse)
async def list_anios(
    grano: str = Query("trimestral", pattern="^(trimestral|anual)$"),
    db=Depends(get_db),
) -> AniosListResponse:
    condicion = "trimestre IS NOT NULL" if grano == "trimestral" else "trimestre IS NULL"
    rows = db.execute(
        text(f"SELECT DISTINCT anio FROM core.dim_tiempo WHERE {condicion} ORDER BY anio")
    ).scalars().all()
    return AniosListResponse(anios=list(rows))


@router.get("/precios", response_model=PrecioListResponse)
async def list_precios(
    id_geografia: Optional[int] = None,
    anio: Optional[int] = None,
    db=Depends(get_db),
) -> PrecioListResponse:
    query = """
        SELECT
            dg.nombre AS nombre_geografia,
            dg.nivel AS nivel_geografia,
            dt.anio,
            dt.trimestre,
            fp.precio_m2
        FROM marts.fact_precio_vivienda fp
        JOIN core.dim_geografia dg ON fp.id_geografia = dg.id_geografia
        JOIN core.dim_tiempo dt ON fp.id_tiempo = dt.id_tiempo
        WHERE (:id_geografia IS NULL OR dg.id_geografia = :id_geografia)
          AND (:anio IS NULL OR dt.anio = :anio)
        ORDER BY dg.nombre, dt.anio, dt.trimestre
    """
    rows = db.execute(text(query), {"id_geografia": id_geografia, "anio": anio}).mappings().all()
    return PrecioListResponse(precios=[PrecioRow(**r) for r in rows])


@router.get("/categorias_indicador", response_model=CategoriasIndicadorListResponse)
async def list_categorias_indicador(db=Depends(get_db)) -> CategoriasIndicadorListResponse:
    rows = db.execute(
        text("SELECT DISTINCT categoria_indicador FROM core.dim_indicador ORDER BY 1")
    ).scalars().all()
    return CategoriasIndicadorListResponse(categorias=list(rows))


@router.get("/indicadores", response_model=IndicadoresListResponse)
async def list_indicadores(
    categoria: Optional[str] = None, db=Depends(get_db)
) -> IndicadoresListResponse:
    query = """
        SELECT id_indicador, nombre_indicador
        FROM core.dim_indicador
        WHERE (:categoria IS NULL OR categoria_indicador = :categoria)
        ORDER BY nombre_indicador
    """
    rows = db.execute(text(query), {"categoria": categoria}).mappings().all()
    return IndicadoresListResponse(indicadores=[IndicadorOption(**r) for r in rows])


@router.get("/indicadores_valores", response_model=IndicadorValorListResponse)
async def list_indicadores_valores(
    id_geografia: Optional[int] = None,
    anio: Optional[int] = None,
    id_indicador: Optional[int] = None,
    db=Depends(get_db),
) -> IndicadorValorListResponse:
    query = """
        SELECT
            dg.nombre AS nombre_geografia,
            dg.nivel AS nivel_geografia,
            dt.anio,
            di.categoria_indicador,
            di.nombre_indicador,
            fi.valor,
            di.unidad
        FROM marts.fact_indicadores_anuales fi
        JOIN core.dim_geografia dg ON fi.id_geografia = dg.id_geografia
        JOIN core.dim_tiempo dt ON fi.id_tiempo = dt.id_tiempo
        JOIN core.dim_indicador di ON fi.id_indicador = di.id_indicador
        WHERE (:id_geografia IS NULL OR dg.id_geografia = :id_geografia)
          AND (:anio IS NULL OR dt.anio = :anio)
          AND (:id_indicador IS NULL OR di.id_indicador = :id_indicador)
        ORDER BY dg.nombre, dt.anio
    """
    rows = db.execute(
        text(query),
        {"id_geografia": id_geografia, "anio": anio, "id_indicador": id_indicador},
    ).mappings().all()
    return IndicadorValorListResponse(valores=[IndicadorValorRow(**r) for r in rows])
