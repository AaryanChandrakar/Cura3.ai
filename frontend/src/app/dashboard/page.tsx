'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import TimeSeriesChart from '@/components/Charts/TimeSeriesChart';
import { getDiagnosisHistory, getMyAnalytics, getDiagnosisTimeSeries } from '@/lib/api';
import styles from './page.module.css';

interface DiagnosisSummary {
    id: string;
    patient_name: string;
    selected_specialists: string[];
    status: string;
    created_at: string;
}

interface Analytics {
    total_reports: number;
    total_diagnoses: number;
    total_chats: number;
    specialist_usage: { specialist: string; count: number }[];
    recent_diagnoses_30d: number;
}

export default function DashboardPage() {
    const { user, loading, isAuthenticated } = useAuth();
    const router = useRouter();
    const [diagnoses, setDiagnoses] = useState<DiagnosisSummary[]>([]);
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [timeSeries, setTimeSeries] = useState<{ date: string; count: number }[]>([]);
    const [pageLoading, setPageLoading] = useState(true);

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push('/');
        }
    }, [loading, isAuthenticated, router]);

    useEffect(() => {
        if (isAuthenticated) {
            Promise.all([
                getDiagnosisHistory().catch(() => ({ diagnoses: [] })),
                getMyAnalytics().catch(() => null),
                getDiagnosisTimeSeries(30).catch(() => ({ series: [] })),
            ]).then(([histRes, analyticsRes, timeSeriesRes]) => {
                setDiagnoses(histRes.diagnoses?.slice(0, 5) || []);
                setAnalytics(analyticsRes);
                setTimeSeries(timeSeriesRes?.series || []);
                setPageLoading(false);
            });
        }
    }, [isAuthenticated]);

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="spinner spinner-lg" />
            </div>
        );
    }

    if (!isAuthenticated) return null;

    const greeting = (() => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good Morning';
        if (hour < 17) return 'Good Afternoon';
        return 'Good Evening';
    })();

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content">
                {/* Welcome */}
                <div className={styles.welcome}>
                    <div>
                        <h1 className="page-title">{greeting}, {user?.name?.split(' ')[0] || 'Doctor'}!</h1>
                        <p className="page-subtitle">Here&apos;s your diagnostic overview.</p>
                    </div>
                    <button onClick={() => router.push('/analyze')} className="btn btn-primary btn-lg">
                        + New Diagnosis
                    </button>
                </div>

                {/* Quick Stats */}
                <div className={styles.statsGrid}>
                    <div className={`card ${styles.statCard}`}>
                        <span className={styles.statIcon}>📋</span>
                        <div className={styles.statInfo}>
                            <span className={styles.statNum}>
                                {pageLoading ? '—' : (analytics?.total_reports ?? 0)}
                            </span>
                            <span className={styles.statLabel}>Reports</span>
                        </div>
                    </div>
                    <div className={`card ${styles.statCard}`}>
                        <span className={styles.statIcon}>🔬</span>
                        <div className={styles.statInfo}>
                            <span className={styles.statNum}>
                                {pageLoading ? '—' : (analytics?.total_diagnoses ?? 0)}
                            </span>
                            <span className={styles.statLabel}>Diagnoses</span>
                        </div>
                    </div>
                    <div className={`card ${styles.statCard}`}>
                        <span className={styles.statIcon}>💬</span>
                        <div className={styles.statInfo}>
                            <span className={styles.statNum}>
                                {pageLoading ? '—' : (analytics?.total_chats ?? 0)}
                            </span>
                            <span className={styles.statLabel}>Chat Sessions</span>
                        </div>
                    </div>
                    <div className={`card ${styles.statCard}`}>
                        <span className={styles.statIcon}>📈</span>
                        <div className={styles.statInfo}>
                            <span className={styles.statNum}>
                                {pageLoading ? '—' : (analytics?.recent_diagnoses_30d ?? 0)}
                            </span>
                            <span className={styles.statLabel}>This Month</span>
                        </div>
                    </div>
                </div>
                {/* Diagnosis Trend Chart */}
                {!pageLoading && timeSeries.length > 0 && (
                    <div className={styles.recentSection}>
                        <h2 className={styles.sectionTitle}>Diagnosis Activity (30 Days)</h2>
                        <div className={`card`} style={{ padding: 'var(--space-5)', marginTop: 'var(--space-4)' }}>
                            <TimeSeriesChart
                                data={timeSeries.map((d) => ({
                                    label: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                                    value: d.count,
                                }))}
                                width={700}
                                height={200}
                                emptyText="No diagnosis activity yet"
                            />
                        </div>
                    </div>
                )}

                {/* Recent Diagnoses */}
                <div className={styles.recentSection}>
                    <div className={styles.sectionTop}>
                        <h2 className={styles.sectionTitle}>Recent Diagnoses</h2>
                        <button onClick={() => router.push('/history')} className="btn btn-ghost btn-sm">
                            View All →
                        </button>
                    </div>

                    {pageLoading ? (
                        <div className={styles.loadingCards}>
                            {[1, 2, 3].map((i) => (
                                <div key={i} className={`card ${styles.skeletonCard}`}>
                                    <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 8 }} />
                                    <div className="skeleton" style={{ height: 14, width: '40%' }} />
                                </div>
                            ))}
                        </div>
                    ) : diagnoses.length > 0 ? (
                        <div className={styles.diagnosisList}>
                            {diagnoses.map((d) => (
                                <div
                                    key={d.id}
                                    className={`card card-interactive ${styles.diagnosisCard}`}
                                    onClick={() => router.push(`/diagnosis/${d.id}`)}
                                >
                                    <div className={styles.diagnosisTop}>
                                        <span className={styles.diagnosisName}>{d.patient_name}</span>
                                        <span className="badge badge-success">{d.status}</span>
                                    </div>
                                    <div className={styles.diagnosisSpecialists}>
                                        {d.selected_specialists?.slice(0, 3).map((s) => (
                                            <span key={s} className="badge badge-primary">{s}</span>
                                        ))}
                                        {(d.selected_specialists?.length || 0) > 3 && (
                                            <span className="badge badge-info">+{d.selected_specialists.length - 3}</span>
                                        )}
                                    </div>
                                    <span className={styles.diagnosisDate}>
                                        {new Date(d.created_at).toLocaleDateString('en-US', {
                                            month: 'short', day: 'numeric', year: 'numeric',
                                        })}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <span className="empty-state-icon">🔬</span>
                            <p>No diagnoses yet. Start by uploading a medical report!</p>
                            <button onClick={() => router.push('/analyze')} className="btn btn-primary" style={{ marginTop: 16 }}>
                                New Diagnosis →
                            </button>
                        </div>
                    )}
                </div>

                {/* Top Specialists */}
                {analytics?.specialist_usage && analytics.specialist_usage.length > 0 && (
                    <div className={styles.recentSection}>
                        <h2 className={styles.sectionTitle}>Most Used Specialists</h2>
                        <div className={styles.specialistBars}>
                            {analytics.specialist_usage.slice(0, 5).map((s) => (
                                <div key={s.specialist} className={styles.specialistBar}>
                                    <span className={styles.specialistName}>{s.specialist}</span>
                                    <div className={styles.barTrack}>
                                        <div
                                            className={styles.barFill}
                                            style={{
                                                width: `${(s.count / (analytics.specialist_usage[0]?.count || 1)) * 100}%`,
                                            }}
                                        />
                                    </div>
                                    <span className={styles.barCount}>{s.count}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
