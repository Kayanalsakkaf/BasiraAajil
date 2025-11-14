import asyncio
import time
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, Document, StageRun, LineageLog, MedallionData
from pipeline_stages import PipelineStages
import json


class DocumentProcessor:
    
    def __init__(self):
        self.stages = [
            ("classify", self.run_classification),
            ("extract", self.run_extraction),
            ("pii_detect", self.run_pii_detection),
            ("validate", self.run_validation),
            ("lineage", self.run_lineage_logging),
            ("medallion", self.run_medallion_promotion)
        ]
    
    async def process_document(self, document_id: str):
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return
            
            context = {
                "document_id": document_id,
                "file_path": document.file_path,
                "document_type": None,
                "extracted_data": None,
                "redacted_data": None,
                "is_valid": False
            }
            
            for stage_name, stage_func in self.stages:
                document.current_stage = stage_name
                db.commit()
                
                stage_run = StageRun(
                    document_id=document_id,
                    stage_name=stage_name,
                    started_at=datetime.utcnow(),
                    status="running"
                )
                db.add(stage_run)
                db.commit()
                
                try:
                    await stage_func(db, stage_run, context)
                    stage_run.status = "completed"
                    stage_run.completed_at = datetime.utcnow()
                except Exception as e:
                    stage_run.status = "failed"
                    stage_run.error_message = str(e)
                    stage_run.completed_at = datetime.utcnow()
                    document.status = "failed"
                    document.error_message = f"Failed at stage {stage_name}: {str(e)}"
                    db.commit()
                    return
                
                db.commit()
            
            document.status = "completed"
            document.current_stage = "completed"
            db.commit()
            
        finally:
            db.close()
    
    async def run_classification(self, db: Session, stage_run: StageRun, context: dict):
        doc_type, output, confidence = await PipelineStages.classify_document(context["file_path"])
        
        context["document_type"] = doc_type
        stage_run.output_data = output
        stage_run.confidence_score = confidence
        
        document = db.query(Document).filter(Document.id == context["document_id"]).first()
        document.document_type = doc_type
    
    async def run_extraction(self, db: Session, stage_run: StageRun, context: dict):
        extracted_data, confidence = await PipelineStages.extract_data(
            context["file_path"],
            context["document_type"]
        )
        
        context["extracted_data"] = extracted_data
        stage_run.output_data = extracted_data
        stage_run.confidence_score = confidence
    
    async def run_pii_detection(self, db: Session, stage_run: StageRun, context: dict):
        pii_result = await PipelineStages.detect_and_redact_pii(context["extracted_data"])
        
        context["redacted_data"] = pii_result["redacted_data"]
        stage_run.output_data = pii_result
        stage_run.confidence_score = 1.0 if pii_result["pii_detected"] else 0.95
    
    async def run_validation(self, db: Session, stage_run: StageRun, context: dict):
        is_valid, passed_rules, failed_rules = await PipelineStages.validate_data(
            context["redacted_data"],
            context["document_type"]
        )
        
        context["is_valid"] = is_valid
        stage_run.output_data = {
            "is_valid": is_valid,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "validation_version": PipelineStages.VALIDATION_VERSION
        }
        stage_run.confidence_score = 1.0 if is_valid else 0.5
    
    async def run_lineage_logging(self, db: Session, stage_run: StageRun, context: dict):
        lineage = LineageLog(
            document_id=context["document_id"],
            timestamp=datetime.utcnow(),
            event_type="PROCESSING_COMPLETED",
            classification_model=PipelineStages.CLASSIFICATION_MODEL,
            extraction_model=PipelineStages.EXTRACTION_MODEL,
            validation_version=PipelineStages.VALIDATION_VERSION,
            execution_arn=f"arn:aws:states:us-east-1:xxx:execution:basira-pipeline:{context['document_id']}",
            event_metadata={
                "document_type": context["document_type"],
                "validation_status": "VALID" if context["is_valid"] else "INVALID"
            }
        )
        db.add(lineage)
        
        stage_run.output_data = {
            "lineage_logged": True,
            "execution_arn": lineage.execution_arn
        }
        stage_run.confidence_score = 1.0
    
    async def run_medallion_promotion(self, db: Session, stage_run: StageRun, context: dict):
        bronze_data = MedallionData(
            document_id=context["document_id"],
            layer="bronze",
            data={
                "source_path": context["file_path"],
                "upload_timestamp": datetime.utcnow().isoformat(),
                "document_metadata": {
                    "document_type": context["document_type"]
                }
            }
        )
        db.add(bronze_data)
        
        silver_data = MedallionData(
            document_id=context["document_id"],
            layer="silver",
            data={
                "redacted_data": context["redacted_data"],
                "pii_redacted": True,
                "extraction_model": PipelineStages.EXTRACTION_MODEL
            }
        )
        db.add(silver_data)
        
        if context["is_valid"]:
            gold_data = MedallionData(
                document_id=context["document_id"],
                layer="gold",
                data={
                    "curated_data": context["redacted_data"],
                    "document_type": context["document_type"],
                    "validation_status": "VALIDATED_SUCCESS",
                    "ready_for_analytics": True
                }
            )
            db.add(gold_data)
        
        stage_run.output_data = {
            "bronze_created": True,
            "silver_created": True,
            "gold_created": context["is_valid"]
        }
        stage_run.confidence_score = 1.0


processor = DocumentProcessor()
