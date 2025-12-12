import { useState, useRef, DragEvent, ChangeEvent } from 'react';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    accept?: string;
    disabled?: boolean;
}

export default function FileUpload({ onFileSelect, accept, disabled }: FileUploadProps) {
    const [isDragOver, setIsDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: DragEvent) => {
        e.preventDefault();
        if (!disabled) {
            setIsDragOver(true);
        }
    };

    const handleDragLeave = (e: DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = (e: DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);

        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            onFileSelect(files[0]);
        }
    };

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            onFileSelect(files[0]);
        }
    };

    const handleClick = () => {
        if (!disabled && inputRef.current) {
            inputRef.current.click();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
        }
    };

    return (
        <div
            className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            onKeyDown={handleKeyDown}
            role="button"
            tabIndex={disabled ? -1 : 0}
            aria-label="Upload file"
            aria-disabled={disabled}
        >
            <input
                ref={inputRef}
                type="file"
                onChange={handleChange}
                accept={accept}
                disabled={disabled}
                aria-hidden="true"
            />

            <svg
                className="upload-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
            >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
            </svg>

            <div className="upload-text">
                <p style={{ margin: 0 }}>
                    <strong>Click to upload</strong> or drag and drop
                </p>
                <p style={{ margin: '0.5rem 0 0', color: 'var(--color-neutral-500)', fontSize: 'var(--font-size-sm)' }}>
                    PDF, Excel, CSV, or log files (max 50MB)
                </p>
            </div>
        </div>
    );
}
