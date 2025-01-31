"""Data ingestion endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db.session import get_db
from services.data_ingestion.data_service import DataIngestionService

router = APIRouter()

class DatasetBase(BaseModel):
    """Base dataset model."""
    name: str
    description: Optional[str] = None
    file_type: str

class DatasetResponse(DatasetBase):
    """Dataset response model."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    row_count: Optional[int] = None
    file_size: Optional[int] = None
    schema: Optional[dict] = None
    error_message: Optional[str] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    dataset: DatasetBase,
    db: AsyncSession = Depends(get_db)
) -> DatasetResponse:
    """Create a new dataset."""
    return await DataIngestionService.create_dataset(
        db=db,
        name=dataset.name,
        description=dataset.description,
        file_type=dataset.file_type
    )

@router.post("/datasets/{dataset_id}/upload")
async def upload_file(
    dataset_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Upload a file to a dataset."""
    # Get dataset
    result = await db.execute(
        "SELECT * FROM datasets WHERE id = :id",
        {"id": dataset_id}
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create upload session
    session = await DataIngestionService.create_upload_session(
        db=db,
        dataset_id=dataset_id,
        filename=file.filename,
        content_type=file.content_type
    )

    # Process file
    success, error = await DataIngestionService.process_file(db, dataset, file)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"message": "File uploaded and processed successfully"}

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
) -> DatasetResponse:
    """Get dataset details."""
    result = await db.execute(
        "SELECT * FROM datasets WHERE id = :id",
        {"id": dataset_id}
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.get("/datasets/{dataset_id}/preview")
async def get_dataset_preview(
    dataset_id: int,
    limit: int = Query(default=10, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """Get a preview of dataset contents."""
    # Check if dataset exists
    result = await db.execute(
        "SELECT * FROM datasets WHERE id = :id",
        {"id": dataset_id}
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Get preview
    return await DataIngestionService.get_dataset_preview(db, dataset_id, limit)

@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[DatasetResponse]:
    """List all datasets."""
    result = await db.execute(
        "SELECT * FROM datasets ORDER BY created_at DESC OFFSET :skip LIMIT :limit",
        {"skip": skip, "limit": limit}
    )
    return result.scalars().all()
