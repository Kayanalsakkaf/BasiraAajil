-- Main table for validated document metadata
CREATE TABLE gold_documents_invoice (
    document_id VARCHAR(255) PRIMARY KEY,
    ingestion_timestamp TIMESTAMPTZ NOT NULL[cite: 77],
    status VARCHAR(50) NOT NULL[cite: 78],
    source_s3_key VARCHAR(1024) NOT NULL[cite: 79],
    
    -- Extracted invoice-level data [cite: 84-90]
    vendor_name VARCHAR(255),
    invoice_number VARCHAR(100),
    invoice_date DATE,
    due_date DATE,
    total_amount DECIMAL(18, 2),
    currency CHAR(3),
    
    -- Foreign key to the operational audit log for full traceability
    FOREIGN KEY (document_id) REFERENCES document_audit_lineage(document_id)
);

-- Table for extracted line items (one-to-many relationship) [cite: 91-104]
CREATE TABLE gold_line_items (
    line_item_id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    description TEXT[cite: 93],
    quantity DECIMAL(10, 2)[cite: 94],
    unit_price DECIMAL(18, 2)[cite: 95],
    total DECIMAL(18, 2)[cite: 96],
    
    FOREIGN KEY (document_id) REFERENCES gold_documents_invoice(document_id)
);

-- Table for validation rules passed (many-to-many relationship) [cite: 80-83]
CREATE TABLE gold_validation_rules (
    rule_id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    rule_name VARCHAR(255) NOT NULL, -- e.g., 'total_matches_line_items'
    
    UNIQUE(document_id, rule_name), -- Prevent duplicate rules per doc
    FOREIGN KEY (document_id) REFERENCES gold_documents_invoice(document_id)
);
