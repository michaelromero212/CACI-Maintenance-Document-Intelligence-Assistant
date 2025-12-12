// API client types for MDIA

export interface Document {
    id: string;
    filename: string;
    file_type: string;
    file_size: number;
    upload_date: string;
    processed: boolean;
    processing_status: string;
    record_count?: number;
    anomaly_count?: number;
    raw_text?: string;
}

export interface ExtractedRecord {
    id: string;
    document_id: string;
    component: string | null;
    system: string | null;
    failure_type: string | null;
    maint_action: string | null;
    priority: 'high' | 'medium' | 'low' | null;
    start_date: string | null;
    end_date: string | null;
    cost_estimate: number | null;
    summary_notes: string | null;
    status: 'open' | 'in-progress' | 'awaiting-parts' | 'complete';
    assigned_to: string | null;
    confidence_score: number | null;
    extraction_method: string | null;
    created_at: string;
    updated_at: string;
}

export interface Anomaly {
    id: string;
    record_id: string | null;
    document_id: string;
    anomaly_type: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
    field_name: string | null;
    field_value: string | null;
    suggested_fix: string | null;
    resolved: boolean;
    created_at: string;
}

export interface StatusUpdateRequest {
    status: 'open' | 'in-progress' | 'awaiting-parts' | 'complete';
    assigned_to?: string;
    notes?: string;
}

export interface StatusOverview {
    total_records: number;
    by_status: Array<{ status: string; count: number }>;
    by_priority: Array<{ status: string; count: number }>;
}

export interface SummaryReport {
    document_id: string;
    filename: string;
    total_records: number;
    status_breakdown: Record<string, number>;
    priority_breakdown: Record<string, number>;
    total_cost_estimate: number | null;
    date_range: { earliest: string; latest: string } | null;
    anomaly_summary: {
        total: number;
        resolved: number;
        unresolved: number;
        by_type: Record<string, number>;
    };
    generated_at: string;
}

export interface CAPReport {
    document_id: string;
    generated_at: string;
    markdown_content: string;
}

export interface LegacyConversionResult {
    success: boolean;
    document_id: string;
    records_created: number;
    records_with_issues: number;
    column_mappings: Record<string, string>;
    message: string;
}
