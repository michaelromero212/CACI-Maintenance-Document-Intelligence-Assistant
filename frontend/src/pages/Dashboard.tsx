import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import { getDocuments, getStatusOverview, deleteDocument } from '../api/client';
import type { Document, StatusOverview } from '../api/types';

export default function Dashboard() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [statusOverview, setStatusOverview] = useState<StatusOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deleting, setDeleting] = useState<string | null>(null);

    useEffect(() => {
        async function loadData() {
            try {
                setLoading(true);
                const [docs, overview] = await Promise.all([
                    getDocuments({ limit: 10 }),
                    getStatusOverview()
                ]);
                setDocuments(docs);
                setStatusOverview(overview);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load data');
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleDelete = async (doc: Document) => {
        if (!confirm(`Delete "${doc.filename}"? This will remove all extracted records and cannot be undone.`)) {
            return;
        }
        try {
            setDeleting(doc.id);
            await deleteDocument(doc.id);
            setDocuments(prev => prev.filter(d => d.id !== doc.id));
            // Refresh the status overview
            const overview = await getStatusOverview();
            setStatusOverview(overview);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Delete failed');
        } finally {
            setDeleting(null);
        }
    };

    if (loading) {
        return (
            <div style={{ padding: 'var(--spacing-6) 0' }}>
                <div className="skeleton" style={{ height: '28px', width: '200px', marginBottom: 'var(--spacing-4)' }}></div>
                <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-4)' }}>
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="card card-body skeleton" style={{ height: '80px' }}></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div style={{ paddingBottom: 'var(--spacing-8)' }}>
            <header className="page-header">
                <div className="flex justify-between items-center">
                    <div>
                        <h1>System Dashboard</h1>
                        <p>Maintenance document processing overview and status summary</p>
                    </div>
                    <Link to="/upload" className="btn btn-primary">
                        + Upload Document
                    </Link>
                </div>
            </header>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-4)' }}>
                    {error}
                </div>
            )}

            {/* Key Metrics */}
            <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-5)' }}>
                <div className="card card-body stat-card">
                    <span className="stat-label">Total Documents</span>
                    <span className="stat-value">{documents.length}</span>
                </div>

                <div className="card card-body stat-card">
                    <span className="stat-label">Total Records</span>
                    <span className="stat-value">{statusOverview?.total_records || 0}</span>
                </div>

                <div className="card card-body stat-card">
                    <span className="stat-label">Open Items</span>
                    <span className="stat-value" style={{ color: 'var(--color-warning-600)' }}>
                        {statusOverview?.by_status.find(s => s.status === 'open')?.count || 0}
                    </span>
                </div>

                <div className="card card-body stat-card">
                    <span className="stat-label">Completed</span>
                    <span className="stat-value" style={{ color: 'var(--color-success-600)' }}>
                        {statusOverview?.by_status.find(s => s.status === 'complete')?.count || 0}
                    </span>
                </div>
            </div>

            {/* Status and Priority Summary */}
            <div className="grid grid-cols-2" style={{ marginBottom: 'var(--spacing-5)' }}>
                {/* Status Breakdown */}
                <div className="card">
                    <div className="card-header">
                        <h3>Status Distribution</h3>
                    </div>
                    <div className="card-body">
                        {statusOverview && statusOverview.by_status.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
                                {statusOverview.by_status.map(({ status, count }) => (
                                    <div
                                        key={status}
                                        style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            padding: 'var(--spacing-2) 0',
                                            borderBottom: '1px solid var(--color-neutral-200)'
                                        }}
                                    >
                                        <StatusBadge status={status} />
                                        <span style={{
                                            fontWeight: 'var(--font-weight-bold)',
                                            fontVariantNumeric: 'tabular-nums'
                                        }}>
                                            {count}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p style={{ color: 'var(--color-neutral-500)', margin: 0 }}>No records processed yet</p>
                        )}
                    </div>
                </div>

                {/* Priority Breakdown */}
                <div className="card">
                    <div className="card-header">
                        <h3>Priority Distribution</h3>
                    </div>
                    <div className="card-body">
                        {statusOverview && statusOverview.by_priority.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
                                {statusOverview.by_priority.map(({ status, count }) => (
                                    <div
                                        key={status}
                                        style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            padding: 'var(--spacing-2) 0',
                                            borderBottom: '1px solid var(--color-neutral-200)'
                                        }}
                                    >
                                        <span style={{
                                            textTransform: 'capitalize',
                                            fontWeight: 'var(--font-weight-medium)'
                                        }}>
                                            {status || 'Unassigned'}
                                        </span>
                                        <span style={{
                                            fontWeight: 'var(--font-weight-bold)',
                                            fontVariantNumeric: 'tabular-nums'
                                        }}>
                                            {count}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p style={{ color: 'var(--color-neutral-500)', margin: 0 }}>No records processed yet</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Document Registry */}
            <div className="card">
                <div className="card-header flex justify-between items-center">
                    <h3>Document Registry</h3>
                    <span style={{
                        fontSize: 'var(--font-size-xs)',
                        color: 'var(--color-neutral-500)'
                    }}>
                        Showing {documents.length} document(s)
                    </span>
                </div>

                {documents.length === 0 ? (
                    <div className="card-body" style={{ textAlign: 'center', padding: 'var(--spacing-8)' }}>
                        <p style={{ color: 'var(--color-neutral-600)', marginBottom: 'var(--spacing-3)' }}>
                            No documents in the system
                        </p>
                        <Link to="/upload" className="btn btn-primary">
                            Upload First Document
                        </Link>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Document Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Status</th>
                                    <th>Records</th>
                                    <th>Anomalies</th>
                                    <th>Upload Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {documents.map(doc => (
                                    <tr key={doc.id}>
                                        <td>
                                            <Link
                                                to={`/documents/${doc.id}`}
                                                style={{ fontWeight: 'var(--font-weight-medium)' }}
                                            >
                                                {doc.filename}
                                            </Link>
                                        </td>
                                        <td>
                                            <code style={{
                                                fontSize: 'var(--font-size-xs)',
                                                background: 'var(--color-neutral-200)',
                                                padding: '2px 6px',
                                                borderRadius: 'var(--radius-sm)'
                                            }}>
                                                {doc.file_type.toUpperCase()}
                                            </code>
                                        </td>
                                        <td style={{ fontVariantNumeric: 'tabular-nums' }}>
                                            {formatFileSize(doc.file_size)}
                                        </td>
                                        <td>
                                            <StatusBadge status={doc.processing_status} />
                                        </td>
                                        <td style={{ fontVariantNumeric: 'tabular-nums', textAlign: 'center' }}>
                                            {doc.record_count || 0}
                                        </td>
                                        <td style={{ fontVariantNumeric: 'tabular-nums', textAlign: 'center' }}>
                                            <span style={{
                                                color: (doc.anomaly_count || 0) > 0 ? 'var(--color-warning-600)' : 'inherit'
                                            }}>
                                                {doc.anomaly_count || 0}
                                            </span>
                                        </td>
                                        <td style={{ whiteSpace: 'nowrap', fontSize: 'var(--font-size-xs)' }}>
                                            {formatDate(doc.upload_date)}
                                        </td>
                                        <td>
                                            <div className="flex gap-2">
                                                <Link
                                                    to={`/documents/${doc.id}`}
                                                    className="btn btn-secondary btn-sm"
                                                >
                                                    View
                                                </Link>
                                                {doc.processed && (
                                                    <Link
                                                        to={`/reports/cap/${doc.id}`}
                                                        className="btn btn-secondary btn-sm"
                                                    >
                                                        CAP
                                                    </Link>
                                                )}
                                                <button
                                                    className="btn btn-sm"
                                                    onClick={() => handleDelete(doc)}
                                                    disabled={deleting === doc.id}
                                                    style={{
                                                        background: 'var(--color-error-100)',
                                                        color: 'var(--color-error-600)',
                                                        border: '1px solid var(--color-error-300)'
                                                    }}
                                                >
                                                    {deleting === doc.id ? '...' : '✕'}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
