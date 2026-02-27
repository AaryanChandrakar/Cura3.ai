'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import { getDiagnosisHistory, deleteDiagnosis } from '@/lib/api';
import styles from './page.module.css';

interface DiagnosisSummary {
    id: string;
    report_id: string;
    patient_name: string;
    selected_specialists: string[];
    status: string;
    created_at: string;
}

export default function HistoryPage() {
    const { loading, isAuthenticated } = useAuth();
    const router = useRouter();

    const [diagnoses, setDiagnoses] = useState<DiagnosisSummary[]>([]);
    const [pageLoading, setPageLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (!loading && !isAuthenticated) router.push('/');
    }, [loading, isAuthenticated, router]);

    useEffect(() => {
        if (isAuthenticated) {
            getDiagnosisHistory()
                .then((res) => {
                    setDiagnoses(res.diagnoses || []);
                    setPageLoading(false);
                })
                .catch(() => setPageLoading(false));
        }
    }, [isAuthenticated]);

    const handleDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Delete this diagnosis and its chat history?')) return;
        try {
            await deleteDiagnosis(id);
            setDiagnoses((prev) => prev.filter((d) => d.id !== id));
        } catch { /* ignore */ }
    };

    const filtered = diagnoses.filter((d) =>
        d.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.selected_specialists.some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()))
    );

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
            <main className="page-content">
                <h1 className="page-title">Diagnosis History</h1>
                <p className="page-subtitle">View and manage your past diagnoses.</p>

                {/* Search */}
                <div className={styles.searchBar}>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="🔍 Search by patient name or specialist..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {pageLoading ? (
                    <div className={styles.list}>
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className={`card ${styles.skeletonCard}`}>
                                <div className="skeleton" style={{ height: 20, width: '50%', marginBottom: 8 }} />
                                <div className="skeleton" style={{ height: 14, width: '35%', marginBottom: 12 }} />
                                <div className="skeleton" style={{ height: 24, width: '80%' }} />
                            </div>
                        ))}
                    </div>
                ) : filtered.length > 0 ? (
                    <div className={styles.list}>
                        {filtered.map((d, i) => (
                            <div
                                key={d.id}
                                className={`card card-interactive ${styles.historyCard}`}
                                onClick={() => router.push(`/diagnosis/${d.id}`)}
                                style={{ animationDelay: `${i * 0.05}s` }}
                            >
                                <div className={styles.cardTop}>
                                    <div>
                                        <h3 className={styles.patientName}>{d.patient_name}</h3>
                                        <span className={styles.cardDate}>
                                            {new Date(d.created_at).toLocaleDateString('en-US', {
                                                month: 'short', day: 'numeric', year: 'numeric',
                                                hour: '2-digit', minute: '2-digit',
                                            })}
                                        </span>
                                    </div>
                                    <div className={styles.cardActions}>
                                        <span className="badge badge-success">{d.status}</span>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            onClick={(e) => handleDelete(d.id, e)}
                                            title="Delete"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                                <div className={styles.specialists}>
                                    {d.selected_specialists.map((s) => (
                                        <span key={s} className="badge badge-primary">{s}</span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <span className="empty-state-icon">📋</span>
                        <p>{searchTerm ? 'No matching diagnoses found.' : 'No diagnoses yet.'}</p>
                        {!searchTerm && (
                            <button onClick={() => router.push('/analyze')} className="btn btn-primary" style={{ marginTop: 16 }}>
                                Run Your First Diagnosis →
                            </button>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
