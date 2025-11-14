from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./basira.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    current_stage = Column(String, default="queued")
    document_type = Column(String, nullable=True)
    status = Column(String, default="processing")
    error_message = Column(Text, nullable=True)


class StageRun(Base):
    __tablename__ = "stage_runs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String, index=True)
    stage_name = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="running")
    output_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)


class LineageLog(Base):
    __tablename__ = "lineage_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    classification_model = Column(String, nullable=True)
    extraction_model = Column(String, nullable=True)
    validation_version = Column(String, nullable=True)
    execution_arn = Column(String, nullable=True)
    event_metadata = Column(JSON, nullable=True)


class MedallionData(Base):
    __tablename__ = "medallion_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String, index=True)
    layer = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
