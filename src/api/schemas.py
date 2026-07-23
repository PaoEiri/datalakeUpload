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
