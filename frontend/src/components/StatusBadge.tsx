interface StatusBadgeProps {
    status: 'open' | 'in-progress' | 'awaiting-parts' | 'complete' | string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
    const statusClass = status.toLowerCase().replace(/\s+/g, '-');
    const displayText = status.replace(/-/g, ' ');

    return (
        <span className={`status-badge status-${statusClass}`}>
            {displayText}
        </span>
    );
}
