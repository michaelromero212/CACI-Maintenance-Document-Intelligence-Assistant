import { useState, useEffect, useCallback } from 'react';
import { getAIStatus } from '../api/client';
import type { AIStatus } from '../api/types';

interface AIStatusIndicatorProps {
    /** Polling interval in milliseconds (default: 30000) */
    pollInterval?: number;
    /** Whether to show extended info on hover */
    showDetails?: boolean;
}

export default function AIStatusIndicator({
    pollInterval = 30000,
    showDetails = true,
}: AIStatusIndicatorProps) {
    const [status, setStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [showTooltip, setShowTooltip] = useState(false);

    const fetchStatus = useCallback(async () => {
        try {
            const result = await getAIStatus();
            setStatus(result);
        } catch (error) {
            setStatus({
                status: 'error',
                model: 'Unknown',
                has_token: false,
                response_time_ms: null,
                last_check: new Date().toISOString(),
                message: 'Failed to connect to backend',
            });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStatus();

        // Set up polling
        const interval = setInterval(fetchStatus, pollInterval);
        return () => clearInterval(interval);
    }, [fetchStatus, pollInterval]);

    const getStatusColor = () => {
        if (loading) return 'var(--color-warning)';
        if (!status) return 'var(--color-text-muted)';

        switch (status.status) {
            case 'connected':
                return 'var(--color-success)';
            case 'disconnected':
                return 'var(--color-danger)';
            case 'error':
                return 'var(--color-danger)';
            default:
                return 'var(--color-text-muted)';
        }
    };

    const getStatusLabel = () => {
        if (loading) return 'Checking...';
        if (!status) return 'Unknown';

        switch (status.status) {
            case 'connected':
                return 'AI Ready';
            case 'disconnected':
                return 'AI Offline';
            case 'error':
                return 'AI Error';
            default:
                return status.status;
        }
    };

    const formatResponseTime = (ms: number | null) => {
        if (ms === null) return 'N/A';
        if (ms < 1000) return `${Math.round(ms)}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    };

    return (
        <div
            className="ai-status-indicator"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            role="status"
            aria-label={`AI Status: ${getStatusLabel()}`}
        >
            <span
                className="ai-status-dot"
                style={{
                    backgroundColor: getStatusColor(),
                    boxShadow: status?.status === 'connected'
                        ? `0 0 8px ${getStatusColor()}`
                        : 'none',
                }}
            />
            <span className="ai-status-label">{getStatusLabel()}</span>

            {showDetails && showTooltip && status && (
                <div className="ai-status-tooltip">
                    <div className="ai-status-tooltip-row">
                        <span className="ai-status-tooltip-label">Model:</span>
                        <span className="ai-status-tooltip-value">
                            {status.model.split('/').pop()}
                        </span>
                    </div>
                    <div className="ai-status-tooltip-row">
                        <span className="ai-status-tooltip-label">Response:</span>
                        <span className="ai-status-tooltip-value">
                            {formatResponseTime(status.response_time_ms)}
                        </span>
                    </div>
                    <div className="ai-status-tooltip-row">
                        <span className="ai-status-tooltip-label">Token:</span>
                        <span className="ai-status-tooltip-value">
                            {status.has_token ? '✓ Configured' : '✗ Missing'}
                        </span>
                    </div>
                    <div className="ai-status-tooltip-message">
                        {status.message}
                    </div>
                </div>
            )}
        </div>
    );
}
