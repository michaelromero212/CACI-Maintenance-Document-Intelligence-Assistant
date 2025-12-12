-- MDIA PostgreSQL Schema
-- Maintenance Document Intelligence Assistant

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table: stores uploaded file metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    raw_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Extracted records table: normalized maintenance data
CREATE TABLE extracted_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    component VARCHAR(255),
    system VARCHAR(255),
    failure_type VARCHAR(255),
    maint_action TEXT,
    priority VARCHAR(50),
    start_date DATE,
    end_date DATE,
    cost_estimate DECIMAL(12, 2),
    summary_notes TEXT,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to VARCHAR(255),
    confidence_score DECIMAL(3, 2),
    extraction_method VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies table: detected data quality issues
CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID REFERENCES extracted_records(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    field_name VARCHAR(100),
    field_value TEXT,
    suggested_fix TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Status updates table: history of status changes
CREATE TABLE status_updates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID REFERENCES extracted_records(id) ON DELETE CASCADE,
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(255),
    notes TEXT,
    updated_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_documents_processed ON documents(processed);
CREATE INDEX idx_documents_upload_date ON documents(upload_date);
CREATE INDEX idx_records_document_id ON extracted_records(document_id);
CREATE INDEX idx_records_status ON extracted_records(status);
CREATE INDEX idx_records_priority ON extracted_records(priority);
CREATE INDEX idx_anomalies_document_id ON anomalies(document_id);
CREATE INDEX idx_anomalies_resolved ON anomalies(resolved);
CREATE INDEX idx_status_updates_record_id ON status_updates(record_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_records_updated_at
    BEFORE UPDATE ON extracted_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
