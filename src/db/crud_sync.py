import os
from typing import Optional, Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Dataset


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


def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
    result = db.execute(select(Dataset).filter_by(id=dataset_id))
    return result.scalar_one_or_none()


def list_datasets(db: Session) -> list[Dataset]:
    result = db.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    return result.scalars().all()
