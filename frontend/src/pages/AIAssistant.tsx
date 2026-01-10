import { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getDocuments, sendAIMessage, getAIAnalysis, getAIStatus } from '../api/client';
import type { Document, AIStatus, AIChatResponse } from '../api/types';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    processingTime?: number;
}

export default function AIAssistant() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [selectedDocumentId, setSelectedDocumentId] = useState<string>('');
    const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load documents and AI status
    useEffect(() => {
        const loadData = async () => {
            try {
                const [docs, status] = await Promise.all([
                    getDocuments({ processed: true }),
                    getAIStatus(),
                ]);
                setDocuments(docs);
                setAiStatus(status);
            } catch (error) {
                console.error('Failed to load data:', error);
            }
        };
        loadData();
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const generateMessageId = () => {
        return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    };

    const handleSendMessage = useCallback(async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage: ChatMessage = {
            id: generateMessageId(),
            role: 'user',
            content: inputMessage.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response: AIChatResponse = await sendAIMessage({
                message: userMessage.content,
                document_id: selectedDocumentId || undefined,
                context: 'maintenance',
            });

            const assistantMessage: ChatMessage = {
                id: generateMessageId(),
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
                processingTime: response.processing_time_ms,
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: ChatMessage = {
                id: generateMessageId(),
                role: 'assistant',
                content: `I apologize, but I encountered an error processing your request. ${error instanceof Error ? error.message : 'Please try again.'}`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [inputMessage, isLoading, selectedDocumentId]);

    const handleQuickAction = useCallback(async (actionType: 'summary' | 'risks' | 'priorities') => {
        if (!selectedDocumentId) {
            alert('Please select a document first');
            return;
        }

        setIsLoading(true);
        const actionLabels = {
            summary: 'Summarizing document...',
            risks: 'Analyzing risks...',
            priorities: 'Identifying priorities...',
        };

        const userMessage: ChatMessage = {
            id: generateMessageId(),
            role: 'user',
            content: `[Quick Action] ${actionLabels[actionType].replace('...', '')}`,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await getAIAnalysis({
                document_id: selectedDocumentId,
                analysis_type: actionType,
            });

            const assistantMessage: ChatMessage = {
                id: generateMessageId(),
                role: 'assistant',
                content: response.analysis,
                timestamp: new Date(),
                processingTime: response.processing_time_ms,
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: ChatMessage = {
                id: generateMessageId(),
                role: 'assistant',
                content: `Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [selectedDocumentId]);

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="ai-assistant-page">
            <header className="page-header">
                <div className="page-header-content">
                    <h1>AI Assistant</h1>
                    <p className="page-description">
                        Chat with the AI to get insights about your maintenance documents
                    </p>
                </div>
                <Link to="/" className="btn btn-secondary">
                    ← Back to Dashboard
                </Link>
            </header>

            <div className="ai-assistant-container">
                {/* Sidebar */}
                <aside className="ai-assistant-sidebar">
                    <div className="ai-sidebar-section">
                        <h3>AI Status</h3>
                        <div className={`ai-sidebar-status ai-sidebar-status--${aiStatus?.status || 'unknown'}`}>
                            <span className="ai-sidebar-status-dot" />
                            <span>{aiStatus?.status === 'connected' ? 'Connected' : 'Disconnected'}</span>
                        </div>
                        {aiStatus && (
                            <p className="ai-sidebar-model">
                                Model: {aiStatus.model.split('/').pop()}
                            </p>
                        )}
                    </div>

                    <div className="ai-sidebar-section">
                        <h3>Document Context</h3>
                        <select
                            value={selectedDocumentId}
                            onChange={(e) => setSelectedDocumentId(e.target.value)}
                            className="ai-document-select"
                        >
                            <option value="">No document selected</option>
                            {documents.map((doc) => (
                                <option key={doc.id} value={doc.id}>
                                    {doc.filename}
                                </option>
                            ))}
                        </select>
                        {selectedDocumentId && (
                            <p className="ai-sidebar-hint">
                                AI responses will be contextualized to this document
                            </p>
                        )}
                    </div>

                    <div className="ai-sidebar-section">
                        <h3>Quick Actions</h3>
                        <div className="ai-quick-actions">
                            <button
                                className="btn btn-outline ai-quick-action-btn"
                                onClick={() => handleQuickAction('summary')}
                                disabled={isLoading || !selectedDocumentId}
                            >
                                📋 Summarize
                            </button>
                            <button
                                className="btn btn-outline ai-quick-action-btn"
                                onClick={() => handleQuickAction('risks')}
                                disabled={isLoading || !selectedDocumentId}
                            >
                                ⚠️ Find Risks
                            </button>
                            <button
                                className="btn btn-outline ai-quick-action-btn"
                                onClick={() => handleQuickAction('priorities')}
                                disabled={isLoading || !selectedDocumentId}
                            >
                                🎯 Prioritize
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Chat Area */}
                <main className="ai-chat-area">
                    <div className="ai-messages-container">
                        {messages.length === 0 ? (
                            <div className="ai-welcome-message">
                                <div className="ai-welcome-icon">🤖</div>
                                <h2>Welcome to MDIA AI Assistant</h2>
                                <p>
                                    I can help you analyze maintenance documents, identify priorities,
                                    and answer questions about your maintenance data.
                                </p>
                                <div className="ai-welcome-suggestions">
                                    <p>Try asking:</p>
                                    <ul>
                                        <li>"What are the highest priority maintenance items?"</li>
                                        <li>"Summarize the current maintenance backlog"</li>
                                        <li>"What equipment needs immediate attention?"</li>
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <div className="ai-messages">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={`ai-message ai-message--${msg.role}`}
                                    >
                                        <div className="ai-message-avatar">
                                            {msg.role === 'user' ? '👤' : '🤖'}
                                        </div>
                                        <div className="ai-message-content">
                                            <div className="ai-message-text">{msg.content}</div>
                                            <div className="ai-message-meta">
                                                <span>{formatTime(msg.timestamp)}</span>
                                                {msg.processingTime && (
                                                    <span className="ai-message-timing">
                                                        • {(msg.processingTime / 1000).toFixed(1)}s
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {isLoading && (
                                    <div className="ai-message ai-message--assistant ai-message--loading">
                                        <div className="ai-message-avatar">🤖</div>
                                        <div className="ai-message-content">
                                            <div className="ai-typing-indicator">
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="ai-input-area">
                        <div className="ai-input-wrapper">
                            <textarea
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask about maintenance documents..."
                                className="ai-input"
                                rows={1}
                                disabled={isLoading}
                            />
                            <button
                                className="btn btn-primary ai-send-btn"
                                onClick={handleSendMessage}
                                disabled={isLoading || !inputMessage.trim()}
                            >
                                {isLoading ? '...' : 'Send'}
                            </button>
                        </div>
                        <p className="ai-input-hint">
                            Press Enter to send, Shift+Enter for new line
                        </p>
                    </div>
                </main>
            </div>
        </div>
    );
}
