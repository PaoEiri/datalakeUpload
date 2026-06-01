import os
import io
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Dataset


async def resolve_dataset_name(session: AsyncSession, original_filename: str) -> str:
    base, ext = os.path.splitext(original_filename)
    candidate = original_filename
    index = 0

    while True:
        result = await session.execute(select(Dataset).filter_by(dataset_name=candidate))
        if result.scalar_one_or_none() is None:
            return candidate
        index += 1
        candidate = f"{base} ({index}){ext}"


async def create_dataset_record(
    session: AsyncSession,
    original_filename: str,
    storage_key: str,
    file_format: str,
    content_type: str,
    size_bytes: int,
    status: str = "pending",
    dataset_name: Optional[str] = None,
) -> Dataset:
    dataset_name = dataset_name or original_filename
    dataset_name = await resolve_dataset_name(session, dataset_name)

    dataset = Dataset(
        dataset_name=dataset_name,
        original_filename=original_filename,
        storage_key=storage_key,
        file_format=file_format,
        content_type=content_type,
        size_bytes=size_bytes,
        status=status,
    )
    session.add(dataset)
    await session.commit()
    await session.refresh(dataset)
    return dataset


async def update_dataset_status(
    session: AsyncSession,
    dataset_id: int,
    status: str,
    row_count: Optional[int] = None,
    column_count: Optional[int] = None,
    schema: Optional[Sequence] = None,
    preview: Optional[Sequence] = None,
    error_message: Optional[str] = None,
) -> Dataset:
    result = await session.execute(select(Dataset).filter_by(id=dataset_id))
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

    await session.commit()
    await session.refresh(dataset)
    return dataset


async def get_dataset(session: AsyncSession, dataset_id: int) -> Optional[Dataset]:
    result = await session.execute(select(Dataset).filter_by(id=dataset_id))
    return result.scalar_one_or_none()


async def list_datasets(session: AsyncSession) -> list[Dataset]:
    result = await session.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    return result.scalars().all()
