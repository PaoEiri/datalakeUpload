from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    id: int
    dataset_name: str
    original_filename: str
    file_format: str
    content_type: str
    size_bytes: int
    status: str
    vigente: bool = True
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    schema_definition: Optional[List[Dict[str, Any]]] = Field(None, alias="schema")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class DatasetCreateResponse(BaseModel):
    id: int
    dataset_name: str
    status: str
    message: str
    id_fuente: Optional[int] = None


class FuenteRegistradaResponse(BaseModel):
    id_fuente: int
    sistema_origen: str
    codigo_fuente: str
    nivel_territorial: str
    stg_modelo_destino: str
    id_dataset_actual: Optional[int] = None
    fecha_ultima_actualizacion: Optional[datetime] = None
    dataset_actual: Optional[DatasetMetadata] = None

    model_config = {
        "from_attributes": True,
    }


class FuentesRegistradasListResponse(BaseModel):
    fuentes: List[FuenteRegistradaResponse]


class ReprocesarFuenteResponse(BaseModel):
    id_fuente: int
    codigo_fuente: str
    stg_modelo_destino: str
    message: str


class DatasetListResponse(BaseModel):
    datasets: List[DatasetMetadata]


class DatasetPreviewResponse(BaseModel):
    dataset_id: int
    dataset_name: str
    preview_rows: List[Dict[str, Any]]
    schema_definition: Optional[List[Dict[str, Any]]] = Field(None, alias="schema")
    row_count: Optional[int] = None
    column_count: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


# ---------------------------------------------------------------------------
# Consulta de datos (solo lectura sobre core.*/marts.*)
# ---------------------------------------------------------------------------
class GeografiaOption(BaseModel):
    id_geografia: int
    nombre: str
    nivel: str


class GeografiasListResponse(BaseModel):
    geografias: List[GeografiaOption]


class AniosListResponse(BaseModel):
    anios: List[int]


class PrecioRow(BaseModel):
    nombre_geografia: str
    nivel_geografia: str
    anio: int
    trimestre: int
    precio_m2: float


class PrecioListResponse(BaseModel):
    precios: List[PrecioRow]


class CategoriasIndicadorListResponse(BaseModel):
    categorias: List[str]


class IndicadorOption(BaseModel):
    id_indicador: int
    nombre_indicador: str


class IndicadoresListResponse(BaseModel):
    indicadores: List[IndicadorOption]


class IndicadorValorRow(BaseModel):
    nombre_geografia: str
    nivel_geografia: str
    anio: int
    categoria_indicador: str
    nombre_indicador: str
    valor: float
    unidad: str


class IndicadorValorListResponse(BaseModel):
    valores: List[IndicadorValorRow]


# ---------------------------------------------------------------------------
# Indicadores de referencia (activar/desactivar aplica_municipal/distrital)
# ---------------------------------------------------------------------------
class IndicadorReferenciaRow(BaseModel):
    indicador_id: int
    nombre_indicador: str
    categoria_indicador: str
    descripcion: str
    aplica_municipal: bool
    aplica_distrital: bool
    usar_en_ml: bool
    cobertura_municipal_pct: Optional[float] = None
    cobertura_distrital_pct: Optional[float] = None
    notas_adaptacion: Optional[str] = None


class IndicadoresReferenciaListResponse(BaseModel):
    indicadores: List[IndicadorReferenciaRow]


class ToggleIndicadorRequest(BaseModel):
    nivel: str = Field(pattern="^(municipal|distrital|ml)$")
    activo: bool


class ToggleIndicadorResponse(BaseModel):
    indicador_id: int
    nivel: str
    activo: bool


class AplicarCambiosResponse(BaseModel):
    message: str


class EditarIndicadorRequest(BaseModel):
    descripcion: str
    notas_adaptacion: Optional[str] = None


class EditarIndicadorResponse(BaseModel):
    indicador_id: int
    descripcion: str
    notas_adaptacion: Optional[str] = None


# ---------------------------------------------------------------------------
# Predicciones (modelo de ML champion)
# ---------------------------------------------------------------------------
class PrediccionRow(BaseModel):
    nombre_geografia: str
    anio: int
    trimestre: int
    precio_predicho: float
    intervalo_inferior: Optional[float] = None
    intervalo_superior: Optional[float] = None
    es_forecast: bool
    version_modelo: str
    algoritmo: str


class PrediccionesListResponse(BaseModel):
    predicciones: List[PrediccionRow]
