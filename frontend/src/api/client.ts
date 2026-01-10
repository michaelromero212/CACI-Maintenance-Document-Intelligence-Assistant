// API client for MDIA backend

import type {
    Document,
    ExtractedRecord,
    StatusUpdateRequest,
    StatusOverview,
    SummaryReport,
    CAPReport,
    LegacyConversionResult,
    AIStatus,
    AIChatRequest,
    AIChatResponse,
    AIAnalyzeRequest,
    AIAnalyzeResponse,
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.status = status;
        this.name = 'ApiError';
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
            errorData.detail || `HTTP error ${response.status}`,
            response.status
        );
    }
    return response.json();
}

// Health check
export async function checkHealth(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse(response);
}

// Documents
export async function getDocuments(params?: {
    skip?: number;
    limit?: number;
    processed?: boolean;
}): Promise<Document[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit));
    if (params?.processed !== undefined) searchParams.set('processed', String(params.processed));

    const response = await fetch(`${API_BASE}/documents?${searchParams}`);
    return handleResponse(response);
}

export async function getDocument(id: string): Promise<Document> {
    const response = await fetch(`${API_BASE}/documents/${id}`);
    return handleResponse(response);
}

export async function uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
    });
    return handleResponse(response);
}

export async function ingestDocument(id: string): Promise<{ message: string; document_id: string; status: string }> {
    const response = await fetch(`${API_BASE}/ingest/${id}`, {
        method: 'POST',
    });
    return handleResponse(response);
}

export async function deleteDocument(id: string): Promise<{ message: string; id: string }> {
    const response = await fetch(`${API_BASE}/documents/${id}`, {
        method: 'DELETE',
    });
    return handleResponse(response);
}

// Legacy conversion
export async function convertLegacyExcel(file: File): Promise<LegacyConversionResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/legacy/convert`, {
        method: 'POST',
        body: formData,
    });
    return handleResponse(response);
}

// Records
export async function getRecords(params?: {
    document_id?: string;
    status?: string;
    priority?: string;
    skip?: number;
    limit?: number;
}): Promise<ExtractedRecord[]> {
    const searchParams = new URLSearchParams();
    if (params?.document_id) searchParams.set('document_id', params.document_id);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.priority) searchParams.set('priority', params.priority);
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit));

    const response = await fetch(`${API_BASE}/records?${searchParams}`);
    return handleResponse(response);
}

export async function getRecord(id: string): Promise<ExtractedRecord> {
    const response = await fetch(`${API_BASE}/record/${id}`);
    return handleResponse(response);
}

export async function updateRecordStatus(
    id: string,
    update: StatusUpdateRequest
): Promise<ExtractedRecord> {
    const response = await fetch(`${API_BASE}/record/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(update),
    });
    return handleResponse(response);
}

// Status
export async function getStatusOverview(): Promise<StatusOverview> {
    const response = await fetch(`${API_BASE}/status/overview`);
    return handleResponse(response);
}

// Reports
export async function getSummaryReport(documentId: string): Promise<SummaryReport> {
    const response = await fetch(`${API_BASE}/report/summary?document_id=${documentId}`);
    return handleResponse(response);
}

export async function getCAPReport(documentId: string): Promise<CAPReport> {
    const response = await fetch(`${API_BASE}/report/cap?document_id=${documentId}`);
    return handleResponse(response);
}

// AI Functions
export async function getAIStatus(): Promise<AIStatus> {
    const response = await fetch(`${API_BASE}/ai/status`);
    return handleResponse(response);
}

export async function sendAIMessage(request: AIChatRequest): Promise<AIChatResponse> {
    const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
    });
    return handleResponse(response);
}

export async function getAIAnalysis(request: AIAnalyzeRequest): Promise<AIAnalyzeResponse> {
    const response = await fetch(`${API_BASE}/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
    });
    return handleResponse(response);
}

export { ApiError };

