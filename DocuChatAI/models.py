from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class DocumentStatus(BaseModel):
    document_id: str
    filename: str
    current_stage: str
    document_type: Optional[str]
    status: str
    upload_timestamp: datetime
    error_message: Optional[str]


class StageRunInfo(BaseModel):
    stage_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    output_data: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    error_message: Optional[str]


class LineageInfo(BaseModel):
    timestamp: datetime
    event_type: str
    classification_model: Optional[str]
    extraction_model: Optional[str]
    validation_version: Optional[str]
    execution_arn: Optional[str]
    event_metadata: Optional[Dict[str, Any]]


class DocumentDetail(BaseModel):
    document: DocumentStatus
    stages: List[StageRunInfo]
    lineage: List[LineageInfo]
    medallion_layers: Dict[str, Any]
