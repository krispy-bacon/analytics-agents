"""Unit tests for data ingestion service."""
import pytest
import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from datetime import datetime
from typing import BinaryIO

from services.data_ingestion.data_service import DataIngestionService
from db.models import Dataset, UploadSession

pytestmark = pytest.mark.asyncio

class MockUploadFile:
    """Mock UploadFile for testing."""
    def __init__(self, file: BinaryIO, filename: str, content_type: str):
        self.file = file
        self.filename = filename
        self.content_type = content_type

    async def read(self):
        """Read file content."""
        return self.file.getvalue()

async def test_create_dataset(test_session):
    """Test dataset creation."""
    dataset = await DataIngestionService.create_dataset(
        db=test_session,
        name="Test Dataset",
        description="Test Description",
        file_type="csv"
    )
    
    assert dataset.id is not None
    assert dataset.name == "Test Dataset"
    assert dataset.description == "Test Description"
    assert dataset.file_type == "csv"
    assert dataset.status == "pending"

async def test_create_upload_session(test_session):
    """Test upload session creation."""
    # Create dataset first
    dataset = await DataIngestionService.create_dataset(
        db=test_session,
        name="Test Dataset",
        description="Test Description",
        file_type="csv"
    )
    
    session = await DataIngestionService.create_upload_session(
        db=test_session,
        dataset_id=dataset.id,
        filename="test.csv",
        content_type="text/csv"
    )
    
    assert session.id is not None
    assert session.dataset_id == dataset.id
    assert session.filename == "test.csv"
    assert session.content_type == "text/csv"
    assert session.status == "uploading"

async def test_process_csv_file(test_session):
    """Test CSV file processing."""
    # Create test CSV data
    csv_data = "name,age\nJohn,30\nJane,25"
    csv_file = BytesIO(csv_data.encode())
    
    # Create dataset
    dataset = await DataIngestionService.create_dataset(
        db=test_session,
        name="Test CSV Dataset",
        description="Test CSV Processing",
        file_type="csv"
    )
    
    # Create upload file
    upload_file = MockUploadFile(
        file=csv_file,
        filename="test.csv",
        content_type="text/csv"
    )
    
    # Process file
    success, error = await DataIngestionService.process_file(
        db=test_session,
        dataset=dataset,
        file=upload_file
    )
    
    assert success is True
    assert error is None
    assert dataset.status == "ready"
    assert dataset.row_count == 2
    assert dataset.schema is not None
    assert dataset.schema["column_count"] == 2
    assert "name" in dataset.schema["columns"]
    assert "age" in dataset.schema["columns"]

async def test_get_dataset_preview(test_session):
    """Test dataset preview retrieval."""
    # Create and process a dataset first
    csv_data = "name,age\nJohn,30\nJane,25"
    csv_file = BytesIO(csv_data.encode())
    
    dataset = await DataIngestionService.create_dataset(
        db=test_session,
        name="Test Preview Dataset",
        description="Test Preview",
        file_type="csv"
    )
    
    # Create upload file
    upload_file = MockUploadFile(
        file=csv_file,
        filename="test.csv",
        content_type="text/csv"
    )
    
    await DataIngestionService.process_file(
        db=test_session,
        dataset=dataset,
        file=upload_file
    )
    
    # Get preview
    preview = await DataIngestionService.get_dataset_preview(
        db=test_session,
        dataset_id=dataset.id,
        limit=2
    )
    
    assert len(preview) == 2
    assert "name" in preview[0]
    assert "age" in preview[0]
    assert preview[0]["name"] in ["John", "Jane"] 