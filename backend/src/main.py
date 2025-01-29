"""Main FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.routes import health, data_ingestion, analytics, auth
from core.config import get_settings
from core.logging import setup_logging
from db.session import init_db
from utils.error_handlers import setup_exception_handlers

settings = get_settings()
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for FastAPI lifespan events."""
    # Startup
    logger.info("Starting up FastAPI application")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application")

app = FastAPI(
    title="AI Analytics Platform API",
    description="REST API for AI-powered data analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(data_ingestion.router, prefix="/data", tags=["Data Ingestion"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint returning API information."""
    return JSONResponse({
        "name": "AI Analytics Platform API",
        "version": "1.0.0",
        "status": "operational"
    })
