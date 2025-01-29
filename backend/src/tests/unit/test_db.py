"""Unit tests for database session management."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from db.session import init_db, get_db

pytestmark = pytest.mark.asyncio

async def test_db_connection(test_session: AsyncSession):
    """Test database connection and basic query execution."""
    result = await test_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1

async def test_init_db():
    """Test database initialization."""
    # Should not raise an exception
    await init_db()

@pytest.mark.asyncio
async def test_get_db():
    """Test database session generator."""
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        # Test that we can execute a query
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1
        break  # We only need to test one session 