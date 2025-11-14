from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid
import os
import asyncio
from datetime import datetime
from typing import List

from database import init_db, get_db, Document, StageRun, LineageLog, MedallionData
from models import DocumentUploadResponse, DocumentStatus, DocumentDetail, StageRunInfo, LineageInfo
from worker import processor

app = FastAPI(title="Basira Document Processing Pipeline")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()


@app.on_event("startup")
async def startup_event():
    print("Basira Pipeline API started")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    document = Document(
        id=document_id,
        filename=file.filename,
        file_path=file_path,
        upload_timestamp=datetime.utcnow(),
        current_stage="queued",
        status="processing"
    )
    db.add(document)
    
    lineage = LineageLog(
        document_id=document_id,
        timestamp=datetime.utcnow(),
        event_type="DOCUMENT_UPLOADED",
        event_metadata={"filename": file.filename, "file_size": len(content)}
    )
    db.add(lineage)
    
    db.commit()
    
    asyncio.create_task(processor.process_document(document_id))
    
    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="processing",
        message="Document uploaded successfully and queued for processing"
    )


@app.get("/api/documents", response_model=List[DocumentStatus])
async def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.upload_timestamp.desc()).all()
    
    return [
        DocumentStatus(
            document_id=doc.id,
            filename=doc.filename,
            current_stage=doc.current_stage,
            document_type=doc.document_type,
            status=doc.status,
            upload_timestamp=doc.upload_timestamp,
            error_message=doc.error_message
        )
        for doc in documents
    ]


@app.get("/api/documents/{document_id}", response_model=DocumentDetail)
async def get_document_detail(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    stages = db.query(StageRun).filter(StageRun.document_id == document_id).order_by(StageRun.started_at).all()
    lineage = db.query(LineageLog).filter(LineageLog.document_id == document_id).order_by(LineageLog.timestamp).all()
    medallion = db.query(MedallionData).filter(MedallionData.document_id == document_id).all()
    
    medallion_layers = {}
    for m in medallion:
        medallion_layers[m.layer] = m.data
    
    return DocumentDetail(
        document=DocumentStatus(
            document_id=document.id,
            filename=document.filename,
            current_stage=document.current_stage,
            document_type=document.document_type,
            status=document.status,
            upload_timestamp=document.upload_timestamp,
            error_message=document.error_message
        ),
        stages=[
            StageRunInfo(
                stage_name=s.stage_name,
                status=s.status,
                started_at=s.started_at,
                completed_at=s.completed_at,
                output_data=s.output_data,
                confidence_score=s.confidence_score,
                error_message=s.error_message
            )
            for s in stages
        ],
        lineage=[
            LineageInfo(
                timestamp=l.timestamp,
                event_type=l.event_type,
                classification_model=l.classification_model,
                extraction_model=l.extraction_model,
                validation_version=l.validation_version,
                execution_arn=l.execution_arn,
                event_metadata=l.event_metadata
            )
            for l in lineage
        ],
        medallion_layers=medallion_layers
    )


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    completed_docs = db.query(Document).filter(Document.status == "completed").count()
    failed_docs = db.query(Document).filter(Document.status == "failed").count()
    processing_docs = db.query(Document).filter(Document.status == "processing").count()
    
    doc_types = db.query(Document.document_type).distinct().all()
    doc_type_counts = {}
    for (doc_type,) in doc_types:
        if doc_type:
            count = db.query(Document).filter(Document.document_type == doc_type).count()
            doc_type_counts[doc_type] = count
    
    return {
        "total_documents": total_docs,
        "completed": completed_docs,
        "failed": failed_docs,
        "processing": processing_docs,
        "document_types": doc_type_counts
    }


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
