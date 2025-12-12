import { useState, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import { getRecords, updateRecordStatus, getStatusOverview } from '../api/client';
import type { ExtractedRecord, StatusOverview } from '../api/types';

type StatusType = 'open' | 'in-progress' | 'awaiting-parts' | 'complete';

export default function StatusBoard() {
    const [records, setRecords] = useState<ExtractedRecord[]>([]);
    const [overview, setOverview] = useState<StatusOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [updating, setUpdating] = useState<string | null>(null);
    const [filterStatus, setFilterStatus] = useState<string>('all');

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            setLoading(true);
            const [recs, ov] = await Promise.all([
                getRecords({ limit: 100 }),
                getStatusOverview()
            ]);
            setRecords(recs);
            setOverview(ov);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
            setLoading(false);
        }
    }

    const handleStatusChange = async (recordId: string, newStatus: StatusType) => {
        try {
            setUpdating(recordId);
            const updated = await updateRecordStatus(recordId, { status: newStatus });
            setRecords(prev =>
                prev.map(r => r.id === recordId ? updated : r)
            );
            const ov = await getStatusOverview();
            setOverview(ov);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Update failed');
        } finally {
            setUpdating(null);
        }
    };

    const handleAssigneeChange = async (recordId: string, assignee: string) => {
        const record = records.find(r => r.id === recordId);
        if (!record) return;

        try {
            setUpdating(recordId);
            const updated = await updateRecordStatus(recordId, {
                status: record.status,
                assigned_to: assignee
            });
            setRecords(prev =>
                prev.map(r => r.id === recordId ? updated : r)
            );
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Update failed');
        } finally {
            setUpdating(null);
        }
    };

    const filteredRecords = filterStatus === 'all'
        ? records
        : records.filter(r => r.status === filterStatus);

    const statusOptions: StatusType[] = ['open', 'in-progress', 'awaiting-parts', 'complete'];

    if (loading) {
        return (
            <div style={{ paddingBottom: 'var(--spacing-8)' }}>
                <div className="skeleton" style={{ height: '28px', width: '200px', marginBottom: 'var(--spacing-4)' }}></div>
                <div className="skeleton" style={{ height: '400px' }}></div>
            </div>
        );
    }

    return (
        <div style={{ paddingBottom: 'var(--spacing-8)' }}>
            <header className="page-header">
                <h1>Maintenance Status Board</h1>
                <p>Track and manage maintenance item status assignments</p>
            </header>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-4)' }}>
                    {error}
                    <button
                        onClick={() => setError(null)}
                        style={{
                            marginLeft: 'var(--spacing-4)',
                            textDecoration: 'underline',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'inherit',
                            fontSize: 'inherit'
                        }}
                    >
                        Dismiss
                    </button>
                </div>
            )}

            {/* Status Filter Cards */}
            {overview && (
                <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-5)' }}>
                    {statusOptions.map(status => {
                        const count = overview.by_status.find(s => s.status === status)?.count || 0;
                        const isActive = filterStatus === status;
                        return (
                            <button
                                key={status}
                                className="card card-body stat-card"
                                onClick={() => setFilterStatus(filterStatus === status ? 'all' : status)}
                                style={{
                                    cursor: 'pointer',
                                    outline: isActive ? '2px solid var(--color-primary-600)' : 'none',
                                    outlineOffset: '-2px',
                                    textAlign: 'left',
                                    border: 'none'
                                }}
                                aria-pressed={isActive}
                            >
                                <StatusBadge status={status} />
                                <span className="stat-value" style={{ marginTop: 'var(--spacing-2)' }}>
                                    {count}
                                </span>
                                {isActive && (
                                    <span style={{
                                        fontSize: 'var(--font-size-xs)',
                                        color: 'var(--color-primary-600)'
                                    }}>
                                        Click to clear filter
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>
            )}

            {/* Records Table */}
            <div className="card">
                <div className="card-header flex justify-between items-center">
                    <h3>
                        Work Items
                        {filterStatus !== 'all' && (
                            <span style={{
                                fontWeight: 'normal',
                                marginLeft: 'var(--spacing-2)',
                                color: 'var(--color-neutral-600)'
                            }}>
                                (filtered: {filterStatus.replace('-', ' ')})
                            </span>
                        )}
                    </h3>
                    <div className="flex gap-2 items-center">
                        <span style={{
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--color-neutral-500)'
                        }}>
                            {filteredRecords.length} item(s)
                        </span>
                        {filterStatus !== 'all' && (
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setFilterStatus('all')}
                            >
                                Clear Filter
                            </button>
                        )}
                    </div>
                </div>

                {filteredRecords.length === 0 ? (
                    <div className="card-body" style={{ textAlign: 'center', padding: 'var(--spacing-8)' }}>
                        <p style={{ color: 'var(--color-neutral-600)' }}>No records found</p>
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
                                    <th>Assigned To</th>
                                    <th>Maintenance Action</th>
                                    <th>Last Updated</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredRecords.map(record => (
                                    <tr key={record.id}>
                                        <td style={{ fontWeight: 'var(--font-weight-medium)' }}>
                                            {record.component || 'Unknown Component'}
                                        </td>
                                        <td style={{ color: 'var(--color-neutral-600)' }}>
                                            {record.system || '-'}
                                        </td>
                                        <td>
                                            <PriorityBadge priority={record.priority} />
                                        </td>
                                        <td>
                                            <select
                                                className="form-select"
                                                value={record.status}
                                                onChange={(e) => handleStatusChange(record.id, e.target.value as StatusType)}
                                                disabled={updating === record.id}
                                                style={{
                                                    minWidth: '130px',
                                                    padding: 'var(--spacing-1) var(--spacing-2)',
                                                    fontSize: 'var(--font-size-xs)'
                                                }}
                                                aria-label={`Status for ${record.component || 'record'}`}
                                            >
                                                {statusOptions.map(status => (
                                                    <option key={status} value={status}>
                                                        {status.replace('-', ' ').toUpperCase()}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                        <td>
                                            <input
                                                type="text"
                                                className="form-input"
                                                placeholder="Assign..."
                                                defaultValue={record.assigned_to || ''}
                                                onBlur={(e) => {
                                                    if (e.target.value !== (record.assigned_to || '')) {
                                                        handleAssigneeChange(record.id, e.target.value);
                                                    }
                                                }}
                                                disabled={updating === record.id}
                                                style={{
                                                    minWidth: '100px',
                                                    padding: 'var(--spacing-1) var(--spacing-2)',
                                                    fontSize: 'var(--font-size-xs)'
                                                }}
                                                aria-label={`Assignee for ${record.component || 'record'}`}
                                            />
                                        </td>
                                        <td style={{
                                            maxWidth: '220px',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap',
                                            fontSize: 'var(--font-size-xs)'
                                        }}>
                                            {record.maint_action || '-'}
                                        </td>
                                        <td style={{
                                            whiteSpace: 'nowrap',
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-neutral-600)'
                                        }}>
                                            {new Date(record.updated_at).toLocaleDateString()}
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
