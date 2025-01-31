"""Integration tests for data ingestion API endpoints."""
import pytest
from httpx import AsyncClient
import pandas as pd
from io import BytesIO

pytestmark = pytest.mark.asyncio

async def test_create_dataset(client: AsyncClient):
    """Test dataset creation endpoint."""
    response = await client.post(
        "/data/datasets",
        json={
            "name": "Test Dataset",
            "description": "Test Description",
            "file_type": "csv"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dataset"
    assert data["description"] == "Test Description"
    assert data["file_type"] == "csv"
    assert data["status"] == "pending"

async def test_upload_file(client: AsyncClient):
    """Test file upload endpoint."""
    # Create dataset first
    dataset_response = await client.post(
        "/data/datasets",
        json={
            "name": "Test Dataset",
            "description": "Test Description",
            "file_type": "csv"
        }
    )
    dataset_id = dataset_response.json()["id"]
    
    # Create test CSV data
    data = {
        "name": ["John", "Jane"],
        "age": [30, 25],
        "city": ["New York", "London"]
    }
    df = pd.DataFrame(data)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Upload file
    response = await client.post(
        f"/data/datasets/{dataset_id}/upload",
        files={"file": ("test.csv", csv_buffer, "text/csv")}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "File uploaded and processed successfully"

async def test_get_dataset(client: AsyncClient):
    """Test get dataset endpoint."""
    # Create dataset first
    create_response = await client.post(
        "/data/datasets",
        json={
            "name": "Test Dataset",
            "description": "Test Description",
            "file_type": "csv"
        }
    )
    dataset_id = create_response.json()["id"]
    
    # Get dataset
    response = await client.get(f"/data/datasets/{dataset_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dataset_id
    assert data["name"] == "Test Dataset"

async def test_get_dataset_preview(client: AsyncClient):
    """Test dataset preview endpoint."""
    # Create dataset
    dataset_response = await client.post(
        "/data/datasets",
        json={
            "name": "Test Dataset",
            "description": "Test Description",
            "file_type": "csv"
        }
    )
    dataset_id = dataset_response.json()["id"]
    
    # Upload file
    data = {
        "name": ["John", "Jane"],
        "age": [30, 25],
        "city": ["New York", "London"]
    }
    df = pd.DataFrame(data)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    await client.post(
        f"/data/datasets/{dataset_id}/upload",
        files={"file": ("test.csv", csv_buffer, "text/csv")}
    )
    
    # Get preview
    response = await client.get(f"/data/datasets/{dataset_id}/preview")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "name" in data[0]
    assert "age" in data[0]
    assert "city" in data[0]

async def test_list_datasets(client: AsyncClient):
    """Test list datasets endpoint."""
    # Create a few datasets
    for i in range(3):
        await client.post(
            "/data/datasets",
            json={
                "name": f"Test Dataset {i}",
                "description": f"Test Description {i}",
                "file_type": "csv"
            }
        )
    
    # List datasets
    response = await client.get("/data/datasets")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # Might be more if other tests created datasets
    assert all(isinstance(d["id"], int) for d in data)
    assert all(d["file_type"] == "csv" for d in data) 