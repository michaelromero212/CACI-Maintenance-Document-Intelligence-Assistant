import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import { uploadDocument, ingestDocument, convertLegacyExcel } from '../api/client';

type UploadMode = 'standard' | 'legacy';

export default function Upload() {
    const navigate = useNavigate();
    const [mode, setMode] = useState<UploadMode>('standard');
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleFileSelect = async (file: File) => {
        setError(null);
        setSuccess(null);
        setUploading(true);

        try {
            if (mode === 'legacy') {
                // Legacy Excel conversion
                const result = await convertLegacyExcel(file);
                setSuccess(result.message);
                setTimeout(() => {
                    navigate(`/documents/${result.document_id}`);
                }, 1500);
            } else {
                // Standard upload + ingestion
                const doc = await uploadDocument(file);
                setSuccess(`Uploaded ${file.name}. Starting processing...`);

                // Trigger ingestion
                await ingestDocument(doc.id);
                setSuccess(`Processing started for ${file.name}`);

                setTimeout(() => {
                    navigate(`/documents/${doc.id}`);
                }, 1500);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div style={{ padding: 'var(--spacing-6) 0' }}>
            <header className="page-header">
                <h1>Upload Document</h1>
                <p>Upload maintenance documents for AI-powered extraction and analysis</p>
            </header>

            {/* Mode Selection */}
            <div className="card" style={{ marginBottom: 'var(--spacing-6)' }}>
                <div className="card-header">
                    <h3>Upload Mode</h3>
                </div>
                <div className="card-body">
                    <div className="flex gap-4">
                        <label
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-2)',
                                cursor: 'pointer'
                            }}
                        >
                            <input
                                type="radio"
                                name="uploadMode"
                                value="standard"
                                checked={mode === 'standard'}
                                onChange={() => setMode('standard')}
                            />
                            <span>
                                <strong>Standard Upload</strong>
                                <br />
                                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-500)' }}>
                                    Upload PDF, Excel, CSV, or log files for AI extraction
                                </span>
                            </span>
                        </label>

                        <label
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-2)',
                                cursor: 'pointer'
                            }}
                        >
                            <input
                                type="radio"
                                name="uploadMode"
                                value="legacy"
                                checked={mode === 'legacy'}
                                onChange={() => setMode('legacy')}
                            />
                            <span>
                                <strong>Legacy Excel Conversion</strong>
                                <br />
                                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-neutral-500)' }}>
                                    Convert old-format MSC maintenance spreadsheets
                                </span>
                            </span>
                        </label>
                    </div>
                </div>
            </div>

            {/* Upload Zone */}
            <div className="card">
                <div className="card-header">
                    <h3>{mode === 'legacy' ? 'Upload Legacy Excel File' : 'Upload Document'}</h3>
                </div>
                <div className="card-body">
                    {error && (
                        <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-4)' }}>
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className="alert alert-success" style={{ marginBottom: 'var(--spacing-4)' }}>
                            {success}
                        </div>
                    )}

                    <FileUpload
                        onFileSelect={handleFileSelect}
                        accept={mode === 'legacy' ? '.xlsx,.xls' : '.pdf,.xlsx,.xls,.csv,.txt,.log'}
                        disabled={uploading}
                    />

                    {uploading && (
                        <div
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: 'var(--spacing-3)',
                                marginTop: 'var(--spacing-4)'
                            }}
                        >
                            <span className="loading-spinner"></span>
                            <span>Processing...</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Info Box */}
            <div className="alert alert-info" style={{ marginTop: 'var(--spacing-6)' }}>
                <strong>Supported File Types:</strong>
                <ul style={{ margin: 'var(--spacing-2) 0 0', paddingLeft: 'var(--spacing-5)' }}>
                    <li>PDF - Maintenance reports, work orders, technical documents</li>
                    <li>Excel (.xlsx, .xls) - Spreadsheets, maintenance logs</li>
                    <li>CSV - Comma-separated data exports</li>
                    <li>Text/Log - Plain text maintenance logs</li>
                </ul>
            </div>
        </div>
    );
}
