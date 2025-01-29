"""Error handling utilities."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database-related errors."""
    return JSONResponse(
        status_code=500,
        content={
            "message": "Database error occurred",
            "detail": str(exc),
            "type": "database_error"
        }
    )

def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the application."""
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
