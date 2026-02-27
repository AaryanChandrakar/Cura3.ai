'use client';

import React, { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import { sendChatMessage, getChatHistory, getDiagnosisHistory } from '@/lib/api';
import styles from './page.module.css';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

interface DiagnosisSummary {
    id: string;
    patient_name: string;
    created_at: string;
}

function ChatContent() {
    const { loading, isAuthenticated } = useAuth();
    const router = useRouter();
    const searchParams = useSearchParams();
    const chatEndRef = useRef<HTMLDivElement>(null);

    const [diagnosisId, setDiagnosisId] = useState(searchParams.get('diagnosis') || '');
    const [diagnoses, setDiagnoses] = useState<DiagnosisSummary[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    useEffect(() => {
        if (!loading && !isAuthenticated) router.push('/');
    }, [loading, isAuthenticated, router]);

    // Load diagnosis list for selector
    useEffect(() => {
        if (isAuthenticated) {
            getDiagnosisHistory()
                .then((res) => setDiagnoses(res.diagnoses || []))
                .catch(() => { });
        }
    }, [isAuthenticated]);

    // Load chat history when diagnosis changes
    useEffect(() => {
        if (diagnosisId && isAuthenticated) {
            setLoadingHistory(true);
            getChatHistory(diagnosisId)
                .then((res) => {
                    setMessages(res.messages || []);
                    setLoadingHistory(false);
                })
                .catch(() => setLoadingHistory(false));
        }
    }, [diagnosisId, isAuthenticated]);

    // Auto-scroll
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || !diagnosisId || sending) return;
        const userMsg = input.trim();
        setInput('');
        setSending(true);

        // Optimistic update
        setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);

        try {
            const result = await sendChatMessage(diagnosisId, userMsg);
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: result.ai_response },
            ]);
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
            ]);
        } finally {
            setSending(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (loading || !isAuthenticated) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="spinner spinner-lg" />
            </div>
        );
    }

    return (
        <div className="page-layout">
            <Sidebar />
            <main className={`page-content ${styles.chatLayout}`}>
                <div className={styles.chatHeader}>
                    <div>
                        <h1 className="page-title">Follow-Up Chat</h1>
                        <p className="page-subtitle">Ask questions about a diagnosis.</p>
                    </div>
                    <select
                        className="input-field"
                        value={diagnosisId}
                        onChange={(e) => {
                            setDiagnosisId(e.target.value);
                            setMessages([]);
                        }}
                        style={{ maxWidth: 300 }}
                    >
                        <option value="">Select a diagnosis...</option>
                        {diagnoses.map((d) => (
                            <option key={d.id} value={d.id}>
                                {d.patient_name} — {new Date(d.created_at).toLocaleDateString()}
                            </option>
                        ))}
                    </select>
                </div>

                {!diagnosisId ? (
                    <div className="empty-state">
                        <span className="empty-state-icon">💬</span>
                        <p>Select a diagnosis to start a follow-up conversation.</p>
                    </div>
                ) : (
                    <>
                        {/* Messages */}
                        <div className={styles.messagesContainer}>
                            {loadingHistory ? (
                                <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
                                    <div className="spinner" />
                                </div>
                            ) : messages.length === 0 ? (
                                <div className={styles.welcomeChat}>
                                    <span style={{ fontSize: '2rem' }}>💬</span>
                                    <h3>Ask anything about this diagnosis</h3>
                                    <p>
                                        Your questions will be answered in context of the specialist reports and final
                                        diagnosis.
                                    </p>
                                    <div className={styles.suggestions}>
                                        {[
                                            'What are the key findings?',
                                            'Which issue is most urgent?',
                                            'What tests should I take next?',
                                        ].map((q) => (
                                            <button
                                                key={q}
                                                className={styles.suggestion}
                                                onClick={() => { setInput(q); }}
                                            >
                                                {q}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                messages.map((msg, i) => (
                                    <div
                                        key={i}
                                        className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.aiMessage}`}
                                    >
                                        <div className={styles.messageAvatar}>
                                            {msg.role === 'user' ? '👤' : '🤖'}
                                        </div>
                                        <div className={styles.messageBubble}>
                                            <pre className={styles.messageText}>{msg.content}</pre>
                                        </div>
                                    </div>
                                ))
                            )}
                            {sending && (
                                <div className={`${styles.message} ${styles.aiMessage}`}>
                                    <div className={styles.messageAvatar}>🤖</div>
                                    <div className={styles.messageBubble}>
                                        <div className="spinner" style={{ width: 18, height: 18 }} />
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Input */}
                        <div className={styles.inputBar}>
                            <textarea
                                className={styles.chatInput}
                                placeholder="Type your question... (Enter to send)"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                rows={1}
                                disabled={sending}
                            />
                            <button
                                className="btn btn-primary"
                                onClick={handleSend}
                                disabled={!input.trim() || sending}
                            >
                                Send →
                            </button>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="spinner spinner-lg" />
            </div>
        }>
            <ChatContent />
        </Suspense>
    );
}
