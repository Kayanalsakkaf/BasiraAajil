# Basira Document Processing Pipeline - Prototype

A demonstration of an event-driven document processing system inspired by the architecture document. This prototype simulates the core concepts of the Basira platform using FastAPI, SQLite, and a web interface.

## Overview

This prototype demonstrates a scalable, multi-stage document processing pipeline that:

- **Accepts PDF document uploads** (simulating S3 uploads)
- **Classifies documents** using keyword-based analysis (simulating AWS Comprehend)
- **Extracts structured data** using PDF parsing (simulating AWS Textract)
- **Detects and redacts PII** using regex patterns (simulating AWS Comprehend PII detection)
- **Validates extracted data** against business rules
- **Tracks lineage** and audit trails for compliance
- **Implements medallion architecture** (Bronze, Silver, Gold layers)

## Architecture

### Pipeline Stages

1. **Queue Stage**: Documents are uploaded and queued for processing
2. **Classification Stage**: Identifies document type (Invoice, National ID, Bank Statement, Payslip, etc.)
3. **Extraction Stage**: Extracts structured data based on document type
4. **PII Detection Stage**: Identifies and redacts sensitive information
5. **Validation Stage**: Applies business rules to verify data quality
6. **Lineage Logging Stage**: Records processing metadata for audit trails
7. **Medallion Promotion Stage**: Organizes data into Bronze/Silver/Gold layers

### Database Schema

- **documents**: Tracks uploaded documents and their current status
- **stage_runs**: Records the execution of each pipeline stage
- **lineage_log**: Maintains audit trail with model versions and execution details
- **medallion_data**: Stores data in Bronze (raw), Silver (cleaned), and Gold (validated) layers

## Features Demonstrated

### 1. Event-Driven Processing
- Async background processing simulates AWS Step Functions workflow
- Documents progress through stages automatically

### 2. AI Model Simulation
- **Classification**: Rule-based keyword matching (simulates ML classifier)
- **Extraction**: Regex-based data extraction from PDFs
- **PII Detection**: Pattern matching for emails, phone numbers, IDs, credit cards, IBANs

### 3. Audit & Compliance
- Complete lineage tracking with model versions
- Execution ARN simulation for traceability
- Business rule validation with pass/fail tracking

### 4. Medallion Architecture
- **Bronze Layer**: Raw document data as ingested
- **Silver Layer**: Cleaned and PII-redacted data
- **Gold Layer**: Validated, analytics-ready data

### 5. Real-Time Visualization
- Live dashboard showing document processing status
- Pipeline stage progression indicators
- Detailed view of extracted data and audit logs

## How to Use

### Upload a Document

1. Open the web interface (automatically displayed)
2. Drag and drop a PDF file or click to browse
3. Watch the document progress through the pipeline stages in real-time

### Sample Documents

Pre-generated sample documents are available in the `sample_docs/` folder:

- **sample_invoice.pdf**: Demonstrates invoice processing with amounts and vendor info
- **sample_national_id.pdf**: Shows ID extraction with PII detection
- **sample_bank_statement.pdf**: Illustrates financial document processing
- **sample_payslip.pdf**: Examples salary and deductions extraction

### View Document Details

Click on any document card to see:
- Extracted data from each stage
- Confidence scores
- PII detection results
- Medallion layer data (Bronze/Silver/Gold)
- Complete audit trail with model versions

## Technical Stack

- **Backend**: FastAPI (Python) - Fast, modern async web framework
- **Database**: SQLite - Lightweight embedded database
- **PDF Processing**: PyPDF2 - PDF text extraction
- **Document Generation**: ReportLab - Sample PDF creation
- **Frontend**: Vanilla JavaScript with modern CSS

## Key Differences from Production

This prototype simulates AWS services locally:

| Production (AWS) | Prototype (Local) |
|-----------------|-------------------|
| S3 ObjectCreated events | File upload endpoint |
| SQS message queue | In-memory task queue |
| Step Functions | Async Python worker |
| AWS Comprehend | Keyword-based classification |
| AWS Textract | PyPDF2 text extraction |
| Comprehend PII | Regex pattern matching |
| DynamoDB | SQLite database |

## Scalability Considerations

The architecture document discusses:

- **Cost Analysis**: Step Functions vs Airflow for 100M+ documents/year
- **PII Handling**: Redaction vs deletion for PDPL compliance
- **Schema Drift**: Challenges with evolving document formats
- **LLM Integration**: Future enhancement for domain-specific reasoning

This prototype demonstrates the core workflow that would scale with:
- AWS Lambda for serverless compute
- SQS for reliable queuing
- DynamoDB for audit logs
- S3 for document storage
- Step Functions for orchestration

## Future Enhancements

Based on the architecture document, potential additions include:

1. **LLM Integration**: Add reasoning capabilities for complex documents
2. **Multi-language Support**: Arabic and English document processing
3. **Human Review Queue**: Low-confidence documents flagged for manual review
4. **Custom Document Types**: Extensible framework for new document categories
5. **Advanced Analytics**: Gold layer queries for business insights

## Files Structure

```
.
├── main.py                 # FastAPI application and API endpoints
├── database.py             # SQLAlchemy models and database setup
├── models.py               # Pydantic models for API requests/responses
├── pipeline_stages.py      # Core processing logic for each stage
├── worker.py               # Background document processor
├── create_sample_pdfs.py   # Generate sample documents
├── static/
│   └── index.html         # Web interface
├── sample_docs/           # Pre-generated sample PDFs
└── uploads/               # User-uploaded documents
```

## API Endpoints

- `GET /` - Web interface
- `POST /api/upload` - Upload a PDF document
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get detailed document information
- `GET /api/stats` - Get system statistics

## Compliance & Security Notes

- PII is detected and redacted before storage in Silver layer
- All processing actions are logged for audit purposes
- Model versions are tracked for reproducibility
- Validation rules ensure data quality before Gold layer promotion
