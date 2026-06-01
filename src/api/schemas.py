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
