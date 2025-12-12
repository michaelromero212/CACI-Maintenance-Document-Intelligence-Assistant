import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSummaryReport } from '../api/client';
import type { SummaryReport as SummaryReportType } from '../api/types';

export default function SummaryReport() {
    const { id } = useParams<{ id: string }>();
    const [report, setReport] = useState<SummaryReportType | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadReport() {
            if (!id) return;

            try {
                setLoading(true);
                const data = await getSummaryReport(id);
                setReport(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load report');
            } finally {
                setLoading(false);
            }
        }
        loadReport();
    }, [id]);

    const formatCurrency = (value: number | null) => {
        if (value === null) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    };

    if (loading) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0' }}>
                <div className="skeleton" style={{ height: '32px', width: '300px', marginBottom: 'var(--spacing-6)' }}></div>
                <div className="skeleton" style={{ height: '400px' }}></div>
            </div>
        );
    }

    if (error || !report) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0', textAlign: 'center' }}>
                <h2>Report Error</h2>
                <p style={{ color: 'var(--color-neutral-500)' }}>
                    {error || 'Report could not be generated'}
                </p>
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
                        <h1>Engineering Summary Report</h1>
                        <p>Document: {report.filename}</p>
                    </div>
                    <div className="flex gap-2">
                        <Link to={`/documents/${id}`} className="btn btn-secondary">
                            View Document
                        </Link>
                        <Link to={`/reports/cap/${id}`} className="btn btn-primary">
                            Generate CAP
                        </Link>
                    </div>
                </div>
            </header>

            {/* Key Metrics */}
            <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-6)' }}>
                <div className="card card-body stat-card">
                    <span className="stat-label">Total Records</span>
                    <span className="stat-value">{report.total_records}</span>
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">Total Cost Estimate</span>
                    <span className="stat-value" style={{ fontSize: 'var(--font-size-xl)' }}>
                        {formatCurrency(report.total_cost_estimate)}
                    </span>
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">Total Anomalies</span>
                    <span className="stat-value">{report.anomaly_summary.total}</span>
                </div>
                <div className="card card-body stat-card">
                    <span className="stat-label">Resolved</span>
                    <span className="stat-value">{report.anomaly_summary.resolved}</span>
                </div>
            </div>

            <div className="grid grid-cols-2" style={{ marginBottom: 'var(--spacing-6)' }}>
                {/* Status Breakdown */}
                <div className="card">
                    <div className="card-header">
                        <h3>Status Breakdown</h3>
                    </div>
                    <div className="card-body">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Status</th>
                                    <th style={{ textAlign: 'right' }}>Count</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(report.status_breakdown).map(([status, count]) => (
                                    <tr key={status}>
                                        <td style={{ textTransform: 'capitalize' }}>{status.replace('-', ' ')}</td>
                                        <td style={{ textAlign: 'right', fontWeight: 'var(--font-weight-semibold)' }}>
                                            {count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Priority Breakdown */}
                <div className="card">
                    <div className="card-header">
                        <h3>Priority Breakdown</h3>
                    </div>
                    <div className="card-body">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Priority</th>
                                    <th style={{ textAlign: 'right' }}>Count</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(report.priority_breakdown).map(([priority, count]) => (
                                    <tr key={priority}>
                                        <td style={{ textTransform: 'capitalize' }}>{priority}</td>
                                        <td style={{ textAlign: 'right', fontWeight: 'var(--font-weight-semibold)' }}>
                                            {count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Date Range */}
            {report.date_range && (
                <div className="card" style={{ marginBottom: 'var(--spacing-6)' }}>
                    <div className="card-header">
                        <h3>Date Range</h3>
                    </div>
                    <div className="card-body">
                        <p style={{ margin: 0 }}>
                            <strong>Earliest:</strong> {report.date_range.earliest} |
                            <strong> Latest:</strong> {report.date_range.latest}
                        </p>
                    </div>
                </div>
            )}

            {/* Anomaly Summary */}
            {report.anomaly_summary.total > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3>Anomaly Summary</h3>
                    </div>
                    <div className="card-body">
                        <div className="grid grid-cols-3" style={{ marginBottom: 'var(--spacing-4)' }}>
                            <div>
                                <span style={{ color: 'var(--color-neutral-500)', fontSize: 'var(--font-size-sm)' }}>
                                    Total
                                </span>
                                <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'var(--font-weight-bold)' }}>
                                    {report.anomaly_summary.total}
                                </div>
                            </div>
                            <div>
                                <span style={{ color: 'var(--color-neutral-500)', fontSize: 'var(--font-size-sm)' }}>
                                    Resolved
                                </span>
                                <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-success-600)' }}>
                                    {report.anomaly_summary.resolved}
                                </div>
                            </div>
                            <div>
                                <span style={{ color: 'var(--color-neutral-500)', fontSize: 'var(--font-size-sm)' }}>
                                    Unresolved
                                </span>
                                <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-warning-600)' }}>
                                    {report.anomaly_summary.unresolved}
                                </div>
                            </div>
                        </div>

                        {Object.keys(report.anomaly_summary.by_type).length > 0 && (
                            <>
                                <h4 style={{ marginTop: 'var(--spacing-4)' }}>By Type</h4>
                                <table className="table">
                                    <tbody>
                                        {Object.entries(report.anomaly_summary.by_type).map(([type, count]) => (
                                            <tr key={type}>
                                                <td style={{ textTransform: 'capitalize' }}>{type.replace('_', ' ')}</td>
                                                <td style={{ textAlign: 'right' }}>{count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div style={{
                marginTop: 'var(--spacing-6)',
                padding: 'var(--spacing-4)',
                background: 'var(--color-neutral-100)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-neutral-500)'
            }}>
                Generated: {new Date(report.generated_at).toLocaleString()}
            </div>
        </div>
    );
}
