import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import { getDocument, getRecords, ingestDocument } from '../api/client';
import type { Document, ExtractedRecord } from '../api/types';

export default function DocumentDetail() {
    const { id } = useParams<{ id: string }>();
    const [document, setDocument] = useState<Document | null>(null);
    const [records, setRecords] = useState<ExtractedRecord[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        loadData();
    }, [id]);

    async function loadData() {
        if (!id) return;

        try {
            setLoading(true);
            const [doc, recs] = await Promise.all([
                getDocument(id),
                getRecords({ document_id: id })
            ]);
            setDocument(doc);
            setRecords(recs);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load document');
        } finally {
            setLoading(false);
        }
    }

    const handleProcess = async () => {
        if (!id) return;

        try {
            setProcessing(true);
            await ingestDocument(id);
            // Reload after a short delay
            setTimeout(loadData, 2000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Processing failed');
        } finally {
            setProcessing(false);
        }
    };

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleDateString();
    };

    const formatCurrency = (value: number | null) => {
        if (value === null) return '-';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    };

    if (loading) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0' }}>
                <div className="skeleton" style={{ height: '32px', width: '300px', marginBottom: 'var(--spacing-6)' }}></div>
                <div className="skeleton" style={{ height: '200px', marginBottom: 'var(--spacing-4)' }}></div>
            </div>
        );
    }

    if (!document) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0', textAlign: 'center' }}>
                <h2>Document Not Found</h2>
                <p>The requested document could not be found.</p>
                <Link to="/" className="btn btn-primary" style={{ marginTop: 'var(--spacing-4)' }}>
                    Return to Dashboard
                </Link>
            </div>
        );
    }

    return (
        <div style={{ padding: 'var(--spacing-6) 0' }}>
            <header className="page-header">
                <div className="flex justify-between items-center">
                    <div>
                        <h1>{document.filename}</h1>
                        <p>
                            Uploaded {new Date(document.upload_date).toLocaleString()} |
                            {' '}{(document.file_size / 1024).toFixed(1)} KB
                        </p>
                    </div>
                    <div className="flex gap-2">
                        {!document.processed && (
                            <button
                                className="btn btn-primary"
                                onClick={handleProcess}
                                disabled={processing}
                            >
                                {processing ? 'Processing...' : 'Process Document'}
                            </button>
                        )}
                        {document.processed && (
                            <>
                                <Link
                                    to={`/reports/summary/${document.id}`}
                                    className="btn btn-secondary"
                                >
                                    View Summary
                                </Link>
                                <Link
                                    to={`/reports/cap/${document.id}`}
                                    className="btn btn-primary"
                                >
                                    Generate CAP
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </header>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>
                    {error}
                </div>
            )}

            {/* Document Info */}
            <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-6)' }}>
                <div className="card card-body stat-card">
                    <span className="stat-label">Status</span>
                    <StatusBadge status={document.processing_status} />
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">File Type</span>
                    <span className="stat-value" style={{ fontSize: 'var(--font-size-xl)', textTransform: 'uppercase' }}>
                        {document.file_type}
                    </span>
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">Records Extracted</span>
                    <span className="stat-value">{records.length}</span>
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">Anomalies</span>
                    <span className="stat-value">{document.anomaly_count || 0}</span>
                </div>
            </div>

            {/* Extracted Records */}
            <div className="card">
                <div className="card-header">
                    <h3>Extracted Records</h3>
                </div>

                {records.length === 0 ? (
                    <div className="card-body" style={{ textAlign: 'center', padding: 'var(--spacing-10)' }}>
                        <p style={{ color: 'var(--color-neutral-500)' }}>
                            {document.processed
                                ? 'No records extracted from this document'
                                : 'Process the document to extract maintenance records'
                            }
                        </p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Component</th>
                                    <th>System</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                    <th>Start</th>
                                    <th>End</th>
                                    <th>Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {records.map(record => (
                                    <tr key={record.id}>
                                        <td style={{ fontWeight: 'var(--font-weight-medium)' }}>
                                            {record.component || '-'}
                                        </td>
                                        <td>{record.system || '-'}</td>
                                        <td>
                                            <PriorityBadge priority={record.priority} />
                                        </td>
                                        <td>
                                            <StatusBadge status={record.status} />
                                        </td>
                                        <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            {record.maint_action || '-'}
                                        </td>
                                        <td>{formatDate(record.start_date)}</td>
                                        <td>{formatDate(record.end_date)}</td>
                                        <td>{formatCurrency(record.cost_estimate)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Raw Text Preview */}
            {document.raw_text && (
                <div className="card" style={{ marginTop: 'var(--spacing-6)' }}>
                    <div className="card-header">
                        <h3>Extracted Text Preview</h3>
                    </div>
                    <div className="card-body">
                        <pre style={{
                            maxHeight: '300px',
                            overflow: 'auto',
                            padding: 'var(--spacing-4)',
                            background: 'var(--color-neutral-100)',
                            borderRadius: 'var(--radius-md)',
                            fontSize: 'var(--font-size-sm)',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word'
                        }}>
                            {document.raw_text.substring(0, 5000)}
                            {document.raw_text.length > 5000 && '...\n[Truncated]'}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
}
