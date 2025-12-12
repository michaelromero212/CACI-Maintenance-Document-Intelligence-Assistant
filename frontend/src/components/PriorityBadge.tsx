interface PriorityBadgeProps {
    priority: 'high' | 'medium' | 'low' | string | null;
}

export default function PriorityBadge({ priority }: PriorityBadgeProps) {
    if (!priority) {
        return <span className="priority-badge priority-low">Unassigned</span>;
    }

    const priorityClass = priority.toLowerCase();

    return (
        <span className={`priority-badge priority-${priorityClass}`}>
            {priority}
        </span>
    );
}
