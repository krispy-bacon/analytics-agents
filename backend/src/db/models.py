"""Database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Dataset(Base):
    """Dataset model for storing metadata about uploaded datasets."""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_type = Column(String, nullable=False)  # csv, excel, json
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    schema = Column(JSON, nullable=True)  # Store column names, types, and metadata
    row_count = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    status = Column(String, nullable=False, default="pending")  # pending, processing, ready, error
    error_message = Column(String, nullable=True)

    # Relationships
    data_points = relationship("DataPoint", back_populates="dataset", cascade="all, delete-orphan")
    upload_sessions = relationship("UploadSession", back_populates="dataset", cascade="all, delete-orphan")

class DataPoint(Base):
    """Model for storing individual data points from datasets."""
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    row_index = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="data_points")

class UploadSession(Base):
    """Model for tracking file upload sessions."""
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    total_chunks = Column(Integer, nullable=True)
    chunks_received = Column(Integer, default=0, nullable=False)
    status = Column(String, nullable=False, default="uploading")  # uploading, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    error_message = Column(String, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="upload_sessions")
