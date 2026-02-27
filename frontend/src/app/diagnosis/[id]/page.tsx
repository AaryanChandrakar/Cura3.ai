'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import { getDiagnosis, deleteDiagnosis, downloadDiagnosisPdf } from '@/lib/api';
import styles from './page.module.css';

interface SpecialistReport {
    specialist_name: string;
    report_content: string;
}

interface DiagnosisData {
    id: string;
    report_id: string;
    patient_name: string;
    selected_specialists: string[];
    specialist_reports: SpecialistReport[];
    final_diagnosis: string;
    status: string;
    created_at: string;
}

const SPECIALIST_ICONS: Record<string, string> = {
    Cardiologist: '❤️', Psychologist: '🧠', Pulmonologist: '🫁',
    Neurologist: '🧬', Endocrinologist: '⚗️', Oncologist: '🔬',
    Dermatologist: '🩺', Gastroenterologist: '🏥', Orthopedist: '🦴',
    'General Practitioner': '👨‍⚕️',
};

export default function DiagnosisDetailPage() {
    const { id } = useParams<{ id: string }>();
    const router = useRouter();
    const { loading, isAuthenticated } = useAuth();

    const [diagnosis, setDiagnosis] = useState<DiagnosisData | null>(null);
    const [pageLoading, setPageLoading] = useState(true);
    const [expandedSpecialist, setExpandedSpecialist] = useState<string | null>(null);
    const [deleting, setDeleting] = useState(false);
    const [downloadingPdf, setDownloadingPdf] = useState(false);

    const handleDownloadPdf = async () => {
        if (!id || !diagnosis) return;
        setDownloadingPdf(true);
        try {
            await downloadDiagnosisPdf(id, diagnosis.patient_name);
        } catch { /* ignore */ }
        setDownloadingPdf(false);
    };

    useEffect(() => {
        if (!loading && !isAuthenticated) router.push('/');
    }, [loading, isAuthenticated, router]);

    useEffect(() => {
        if (isAuthenticated && id) {
            getDiagnosis(id)
                .then((data) => {
                    setDiagnosis(data);
                    setPageLoading(false);
                })
                .catch(() => {
                    setPageLoading(false);
                });
        }
    }, [isAuthenticated, id]);

    const handleDelete = async () => {
        if (!id || !confirm('Are you sure you want to delete this diagnosis?')) return;
        setDeleting(true);
        try {
            await deleteDiagnosis(id);
            router.push('/history');
        } catch {
            setDeleting(false);
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
            <main className="page-content">
                {pageLoading ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
                        <div className="spinner spinner-lg" />
                    </div>
                ) : !diagnosis ? (
                    <div className="empty-state">
                        <span className="empty-state-icon">🔍</span>
                        <p>Diagnosis not found.</p>
                        <button onClick={() => router.push('/history')} className="btn btn-primary" style={{ marginTop: 16 }}>
                            ← Back to History
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Header */}
                        <div className={styles.header}>
                            <div>
                                <button onClick={() => router.push('/history')} className="btn btn-ghost btn-sm" style={{ marginBottom: 8 }}>
                                    ← Back to History
                                </button>
                                <h1 className="page-title">{diagnosis.patient_name}</h1>
                                <p className="page-subtitle">
                                    Diagnosed on {new Date(diagnosis.created_at).toLocaleDateString('en-US', {
                                        weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
                                    })}
                                </p>
                            </div>
                            <div className={styles.headerActions}>
                                <button
                                    className="btn btn-outline"
                                    onClick={handleDownloadPdf}
                                    disabled={downloadingPdf}
                                >
                                    {downloadingPdf ? '⏳ Generating...' : '📥 Download PDF'}
                                </button>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => router.push(`/chat?diagnosis=${id}`)}
                                >
                                    💬 Ask Follow-Up
                                </button>
                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={handleDelete}
                                    disabled={deleting}
                                >
                                    {deleting ? 'Deleting...' : '🗑️ Delete'}
                                </button>
                            </div>
                        </div>

                        {/* Specialists Used */}
                        <div className={styles.specialistsUsed}>
                            {diagnosis.selected_specialists.map((s) => (
                                <span key={s} className="badge badge-primary">
                                    {SPECIALIST_ICONS[s] || '👨‍⚕️'} {s}
                                </span>
                            ))}
                        </div>

                        {/* Final Diagnosis */}
                        <div className={`card ${styles.diagnosisBlock}`}>
                            <h2 className={styles.blockTitle}>📋 Final Diagnosis Report</h2>
                            <pre className={styles.diagnosisText}>{diagnosis.final_diagnosis}</pre>
                        </div>

                        {/* Individual Specialist Reports */}
                        <h2 className={styles.sectionTitle}>Individual Specialist Reports</h2>
                        <div className={styles.specialistReports}>
                            {diagnosis.specialist_reports.map((sr) => (
                                <div key={sr.specialist_name} className={`card ${styles.specialistCard}`}>
                                    <button
                                        className={styles.specialistHeader}
                                        onClick={() =>
                                            setExpandedSpecialist(
                                                expandedSpecialist === sr.specialist_name ? null : sr.specialist_name
                                            )
                                        }
                                    >
                                        <div className={styles.specialistInfo}>
                                            <span className={styles.specialistIcon}>
                                                {SPECIALIST_ICONS[sr.specialist_name] || '👨‍⚕️'}
                                            </span>
                                            <span className={styles.specialistName}>{sr.specialist_name}</span>
                                        </div>
                                        <span className={styles.expandIcon}>
                                            {expandedSpecialist === sr.specialist_name ? '▼' : '▶'}
                                        </span>
                                    </button>
                                    {expandedSpecialist === sr.specialist_name && (
                                        <div className={styles.specialistContent}>
                                            <pre className={styles.reportText}>{sr.report_content}</pre>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Disclaimer */}
                        <div className="alert alert-warning" style={{ marginTop: 32 }}>
                            <span>⚠️</span>
                            <span>
                                <strong>Disclaimer:</strong> This report is generated by AI for research and educational
                                purposes only. It is NOT a substitute for professional medical advice, diagnosis,
                                or treatment. Always consult a qualified healthcare provider.
                            </span>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
