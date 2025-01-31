"""Data ingestion service module."""
import pandas as pd
import json
from typing import Tuple, List, Dict, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.models import Dataset, UploadSession, DataPoint

class DataIngestionService:
    """Service for handling data ingestion operations."""

    ALLOWED_FILE_TYPES = {
        'csv': ['text/csv', 'application/csv'],
        'excel': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                 'application/vnd.ms-excel'],
        'json': ['application/json']
    }

    @staticmethod
    async def create_dataset(
        db: AsyncSession,
        name: str,
        description: Optional[str],
        file_type: str
    ) -> Dataset:
        """Create a new dataset entry."""
        dataset = Dataset(
            name=name,
            description=description,
            file_type=file_type,
            status="pending"
        )
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        return dataset

    @staticmethod
    async def create_upload_session(
        db: AsyncSession,
        dataset_id: int,
        filename: str,
        content_type: str
    ) -> UploadSession:
        """Create a new upload session."""
        session = UploadSession(
            dataset_id=dataset_id,
            filename=filename,
            content_type=content_type,
            status="uploading"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def process_file(
        db: AsyncSession,
        dataset: Dataset,
        file: UploadFile
    ) -> Tuple[bool, Optional[str]]:
        """Process uploaded file and store data."""
        try:
            # Update dataset status
            dataset.status = "processing"
            await db.commit()

            # Read file content based on type
            df = await DataIngestionService._read_file(file, dataset.file_type)
            
            # Infer and store schema
            schema = DataIngestionService._infer_schema(df)
            dataset.schema = schema
            dataset.row_count = len(df)
            
            # Store data points in chunks
            chunk_size = 1000
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                data_points = [
                    DataPoint(
                        dataset_id=dataset.id,
                        row_index=j + i,
                        data=row.to_dict()
                    )
                    for j, row in chunk.iterrows()
                ]
                db.add_all(data_points)
                await db.commit()

            # Update dataset status
            dataset.status = "ready"
            await db.commit()
            return True, None

        except Exception as e:
            dataset.status = "error"
            dataset.error_message = str(e)
            await db.commit()
            return False, str(e)

    @staticmethod
    async def _read_file(file: UploadFile, file_type: str) -> pd.DataFrame:
        """Read file content into pandas DataFrame."""
        content = await file.read()
        
        if file_type == 'csv':
            return pd.read_csv(pd.io.common.BytesIO(content))
        elif file_type == 'excel':
            return pd.read_excel(pd.io.common.BytesIO(content))
        elif file_type == 'json':
            return pd.read_json(pd.io.common.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _infer_schema(df: pd.DataFrame) -> Dict:
        """Infer schema from DataFrame."""
        schema = {
            'columns': {},
            'row_count': len(df),
            'column_count': len(df.columns)
        }

        for column in df.columns:
            dtype = str(df[column].dtype)
            sample = df[column].iloc[0] if not df.empty else None
            unique_count = df[column].nunique()
            null_count = df[column].isna().sum()

            schema['columns'][column] = {
                'type': dtype,
                'sample': str(sample) if sample is not None else None,
                'unique_count': int(unique_count),
                'null_count': int(null_count)
            }

        return schema

    @staticmethod
    async def get_dataset_preview(
        db: AsyncSession,
        dataset_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get a preview of dataset contents."""
        result = await db.execute(
            text("""
                SELECT data 
                FROM data_points 
                WHERE dataset_id = :dataset_id 
                ORDER BY row_index 
                LIMIT :limit
            """),
            {"dataset_id": dataset_id, "limit": limit}
        )
        rows = result.scalars().all()
        return [row for row in rows] 