"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
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
        result = await db.execute(text("SELECT 1"))
        await db.commit()
        db_connected = result.scalar() == 1
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        db_connected = False
    
    return HealthResponse(
        status="operational",
        timestamp=datetime.utcnow(),
        database_connected=db_connected
    )
