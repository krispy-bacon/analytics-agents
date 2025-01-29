"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from db.session import get_db

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    database_connected: bool
    version: str = "1.0.0"

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Check the health of the API and its dependencies.
    
    Returns:
        HealthResponse: Health status information including database connectivity.
    """
    try:
        # Verify database connection
        await db.execute("SELECT 1")
        db_connected = True
    except Exception:
        db_connected = False
    
    return HealthResponse(
        status="operational",
        timestamp=datetime.utcnow(),
        database_connected=db_connected
    )
