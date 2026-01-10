import { Component, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

/**
 * Error Boundary component to catch JavaScript errors in child components.
 * 
 * Prevents the entire app from crashing when a component throws an error.
 * Instead, displays a user-friendly fallback UI.
 */
export default class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        // Update state so the next render shows the fallback UI
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
        // Log error to console for debugging
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    handleReset = (): void => {
        this.setState({ hasError: false, error: null });
    };

    render(): ReactNode {
        if (this.state.hasError) {
            // Custom fallback if provided
            if (this.props.fallback) {
                return this.props.fallback;
            }

            // Default fallback UI
            return (
                <div className="error-boundary">
                    <div className="error-boundary-content">
                        <h2 className="error-boundary-title">
                            ⚠️ Something went wrong
                        </h2>
                        <p className="error-boundary-message">
                            We encountered an unexpected error. Please try refreshing the page.
                        </p>
                        {this.state.error && (
                            <details className="error-boundary-details">
                                <summary>Error details</summary>
                                <pre>{this.state.error.message}</pre>
                            </details>
                        )}
                        <div className="error-boundary-actions">
                            <button
                                className="btn btn-primary"
                                onClick={() => window.location.reload()}
                            >
                                Refresh Page
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={this.handleReset}
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
