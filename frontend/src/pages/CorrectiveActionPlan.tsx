import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCAPReport } from '../api/client';
import type { CAPReport as CAPReportType } from '../api/types';

export default function CorrectiveActionPlan() {
    const { id } = useParams<{ id: string }>();
    const [report, setReport] = useState<CAPReportType | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        async function loadReport() {
            if (!id) return;

            try {
                setLoading(true);
                const data = await getCAPReport(id);
                setReport(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to generate CAP');
            } finally {
                setLoading(false);
            }
        }
        loadReport();
    }, [id]);

    const handleCopy = async () => {
        if (!report) return;

        try {
            await navigator.clipboard.writeText(report.markdown_content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = report.markdown_content;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    // Simple markdown to HTML conversion
    const renderMarkdown = (md: string) => {
        let html = md
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Horizontal rule
            .replace(/^---$/gim, '<hr />')
            // Tables (basic support)
            .replace(/\|(.+)\|/g, (match) => {
                const cells = match.split('|').filter(c => c.trim());
                if (cells.every(c => /^[\s\-:]+$/.test(c))) {
                    return ''; // Skip separator row
                }
                const cellsHtml = cells.map(c => `<td>${c.trim()}</td>`).join('');
                return `<tr>${cellsHtml}</tr>`;
            })
            // Lists
            .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            // Line breaks
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br />');

        // Wrap in paragraph
        html = `<p>${html}</p>`;

        // Fix list wrapping
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');

        // Fix table wrapping
        html = html.replace(/(<tr>.*?<\/tr>)+/g, '<table>$&</table>');

        return html;
    };

    if (loading) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0' }}>
                <div className="skeleton" style={{ height: '32px', width: '300px', marginBottom: 'var(--spacing-6)' }}></div>
                <div style={{ textAlign: 'center', padding: 'var(--spacing-10)' }}>
                    <span className="loading-spinner" style={{ width: '40px', height: '40px' }}></span>
                    <p style={{ marginTop: 'var(--spacing-4)', color: 'var(--color-neutral-500)' }}>
                        Generating Corrective Action Plan...
                    </p>
                </div>
            </div>
        );
    }

    if (error || !report) {
        return (
            <div style={{ padding: 'var(--spacing-8) 0', textAlign: 'center' }}>
                <h2>Generation Error</h2>
                <p style={{ color: 'var(--color-neutral-500)' }}>
                    {error || 'CAP could not be generated. Please ensure the document has been processed.'}
                </p>
                <Link to={`/documents/${id}`} className="btn btn-primary" style={{ marginTop: 'var(--spacing-4)' }}>
                    Return to Document
                </Link>
            </div>
        );
    }

    return (
        <div style={{ padding: 'var(--spacing-6) 0' }}>
            <header className="page-header">
                <div className="flex justify-between items-center">
                    <div>
                        <h1>Corrective Action Plan</h1>
                        <p>Generated: {new Date(report.generated_at).toLocaleString()}</p>
                    </div>
                    <div className="flex gap-2">
                        <Link to={`/documents/${id}`} className="btn btn-secondary">
                            View Document
                        </Link>
                        <button
                            className={`btn ${copied ? 'btn-success' : 'btn-primary'}`}
                            onClick={handleCopy}
                        >
                            {copied ? 'Copied!' : 'Copy to Clipboard'}
                        </button>
                    </div>
                </div>
            </header>

            {/* CAP Content */}
            <div className="card">
                <div className="card-body markdown-content">
                    <div
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(report.markdown_content) }}
                    />
                </div>
            </div>

            {/* Raw Markdown (Collapsible) */}
            <details style={{ marginTop: 'var(--spacing-6)' }}>
                <summary style={{
                    cursor: 'pointer',
                    padding: 'var(--spacing-3)',
                    background: 'var(--color-neutral-100)',
                    borderRadius: 'var(--radius-md)',
                    fontWeight: 'var(--font-weight-medium)'
                }}>
                    View Raw Markdown
                </summary>
                <pre style={{
                    marginTop: 'var(--spacing-2)',
                    padding: 'var(--spacing-4)',
                    background: 'var(--color-neutral-800)',
                    color: 'var(--color-neutral-100)',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'auto',
                    fontSize: 'var(--font-size-sm)',
                    whiteSpace: 'pre-wrap'
                }}>
                    {report.markdown_content}
                </pre>
            </details>
        </div>
    );
}
