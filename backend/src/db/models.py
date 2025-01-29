"""Database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

class DatasetType(str, enum.Enum):
    """Dataset types enumeration."""
    CSV = "csv"
    JSON = "json"
    SQL = "sql"
    API = "api"

class AnalysisStatus(str, enum.Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    datasets: Mapped[list["Dataset"]] = relationship(back_populates="user")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="user")

class Dataset(Base):
    """Dataset model."""
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    type: Mapped[DatasetType] = mapped_column(SQLEnum(DatasetType))
    source_path: Mapped[str] = mapped_column(String(1000))
    dataset_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="datasets")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="dataset")

class Analysis(Base):
    """Analysis model."""
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    status: Mapped[AnalysisStatus] = mapped_column(
        SQLEnum(AnalysisStatus),
        default=AnalysisStatus.PENDING
    )
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="analyses")
    dataset: Mapped["Dataset"] = relationship(back_populates="analyses")
    results: Mapped[list["Result"]] = relationship(back_populates="analysis")

class Result(Base):
    """Analysis result model."""
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    output: Mapped[dict] = mapped_column(JSON)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Foreign keys
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))

    # Relationships
    analysis: Mapped["Analysis"] = relationship(back_populates="results")
