# Basira Pipeline Demo Guide

## Quick Start Demo

### Step 1: Upload a Sample Document

The system includes 4 pre-generated sample PDFs in the `sample_docs/` folder:

1. **sample_invoice.pdf** - Contains vendor info, line items, and amounts
2. **sample_national_id.pdf** - Has PII like ID numbers and personal details
3. **sample_bank_statement.pdf** - Includes account numbers and transactions
4. **sample_payslip.pdf** - Shows salary and deductions

To test the pipeline:
1. Click the upload area in the web interface
2. Select any sample PDF from the `sample_docs/` folder
3. Watch the document progress through the 6 pipeline stages in real-time

### Step 2: Watch Real-Time Processing

The document will automatically progress through these stages:

1. **classify** (0.5s) - Identifies document type using keyword analysis
2. **extract** (0.8s) - Extracts structured data from the PDF
3. **pii_detect** (0.3s) - Finds and redacts sensitive information
4. **validate** (0.4s) - Applies business rules validation
5. **lineage** (instant) - Logs audit trail with model versions
6. **medallion** (instant) - Promotes data to Bronze/Silver/Gold layers

Total processing time: ~2 seconds per document

### Step 3: View Detailed Results

Click on any processed document to see:

**Document Information:**
- Filename, type, status, upload timestamp

**Pipeline Stages:**
- Each stage's output data with confidence scores
- Model versions used (simulating AWS service versions)

**Medallion Architecture:**
- **Bronze Layer**: Raw uploaded document data
- **Silver Layer**: PII-redacted, cleaned data
- **Gold Layer**: Validated, analytics-ready data (only for valid documents)

**Lineage & Audit Trail:**
- Complete processing history
- Model versions (classification, extraction, validation)
- Execution ARNs for traceability
- Event timestamps

## What Each Document Type Demonstrates

### Invoice Processing
- **Classification**: Detects keywords like "invoice", "amount due", "vendor"
- **Extraction**: Pulls vendor name, invoice number, amounts, line items
- **Validation**: Checks for mandatory fields (total amount, vendor, invoice number)
- **PII**: May detect email addresses or payment IBANs

### National ID Processing
- **Classification**: Identifies ID-specific keywords
- **Extraction**: Captures ID number, name, date of birth
- **PII Detection**: Redacts ID numbers (10-digit Saudi IDs)
- **Validation**: Ensures ID number and name are present

### Bank Statement Processing
- **Classification**: Recognizes bank statement terminology
- **Extraction**: Gets account number, balances, transactions
- **PII**: Detects and redacts account numbers, IBANs
- **Validation**: Checks for account number presence

### Payslip Processing
- **Classification**: Matches salary-related keywords
- **Extraction**: Pulls employee info, salary amounts, deductions
- **PII**: May redact employee IDs or personal details
- **Validation**: Verifies salary amounts are present

## Key Features to Explore

### 1. Dashboard Statistics
- Real-time counts of total, completed, processing, and failed documents
- Document type breakdown

### 2. Pipeline Visualization
- Color-coded stage indicators:
  - **Gray**: Not started
  - **Blue**: Currently processing
  - **Green**: Completed successfully
  - **Red**: Failed

### 3. Confidence Scores
Each AI operation includes a confidence score:
- Classification: 60-95% based on keyword matches
- Extraction: 75-95% with random variance
- PII Detection: 95-100% based on patterns found
- Validation: 100% if valid, 50% if invalid

### 4. PII Redaction
Look for `[REDACTED-EMAIL]`, `[REDACTED-PHONE]`, `[REDACTED-NATIONAL_ID]` in the Silver layer data

### 5. Model Versioning
All operations track which model version was used:
- `v1.2-comprehend-classifier`
- `textract-analyze-v3.0`
- `v2.1-business-rules`
- `aws-comprehend-pii-v2.0`

## Testing Different Scenarios

### Successful Processing
Upload any of the 4 sample documents - they all contain enough data to pass validation

### Validation Failures
The system validates:
- Invoices must have: vendor name, invoice number, total amount
- IDs must have: ID number, name
- Bank statements must have: account number

### PII Detection
Watch the difference between Bronze (raw) and Silver (redacted) layers to see PII protection in action

## Production Readiness Indicators

This prototype demonstrates production-ready concepts:

✅ **Event-driven architecture** - Async processing pipeline
✅ **Audit trails** - Complete lineage with model versions
✅ **Data governance** - Medallion architecture (Bronze/Silver/Gold)
✅ **PII compliance** - Automated detection and redaction
✅ **Validation** - Business rules enforcement
✅ **Scalability** - Stage-based processing pattern
✅ **Traceability** - Execution ARNs and timestamps

## Architecture Alignment

This prototype implements concepts from the architecture document:

- ✅ Queue stage (simulated with async processing)
- ✅ Classification stage (keyword-based ML simulation)
- ✅ Extraction stage (PDF parsing simulating Textract)
- ✅ PII detection and redaction (regex-based)
- ✅ Validation with business rules
- ✅ Lineage tracking with model versions
- ✅ Medallion architecture (Bronze/Silver/Gold)
- ✅ Step Function workflow (simulated with async Python)

## Next Steps for Production

From the architecture document, production deployment would add:

1. **AWS Integration**: Replace local services with AWS (S3, SQS, Step Functions, Textract, Comprehend)
2. **LLM Reasoning**: Add domain-specific understanding for complex documents
3. **Human Review Queue**: Route low-confidence documents for manual review
4. **Multi-language Support**: Handle Arabic and English documents
5. **Custom Document Types**: Extend classification for business-specific documents
6. **Scale Testing**: Validate with thousands of documents per day
7. **Cost Optimization**: Implement the Step Functions vs Airflow decision based on volume
