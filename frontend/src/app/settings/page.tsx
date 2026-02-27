'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar/Sidebar';
import styles from './page.module.css';

export default function SettingsPage() {
    const { user, loading, isAuthenticated, logout } = useAuth();
    const router = useRouter();

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
                <div className="spinner spinner-lg" />
            </div>
        );
    }

    if (!isAuthenticated) {
        router.push('/');
        return null;
    }

    return (
        <div className="page-layout">
            <Sidebar />
            <main className="page-content">
                <h1 className="page-title">Settings</h1>
                <p className="page-subtitle">Manage your account and preferences.</p>

                {/* Profile Card */}
                <div className={`card ${styles.profileCard}`}>
                    <h2 className={styles.cardTitle}>👤 Profile</h2>
                    <div className={styles.profileInfo}>
                        <div className={styles.avatar}>
                            {user?.avatar_url ? (
                                // eslint-disable-next-line @next/next/no-img-element
                                <img src={user.avatar_url} alt={user.name} className={styles.avatarImg} />
                            ) : (
                                <span className={styles.avatarFallback}>
                                    {user?.name?.charAt(0)?.toUpperCase() || '?'}
                                </span>
                            )}
                        </div>
                        <div className={styles.profileMeta}>
                            <div className={styles.field}>
                                <span className={styles.fieldLabel}>Name</span>
                                <span className={styles.fieldValue}>{user?.name || '—'}</span>
                            </div>
                            <div className={styles.field}>
                                <span className={styles.fieldLabel}>Email</span>
                                <span className={styles.fieldValue}>{user?.email || '—'}</span>
                            </div>
                            <div className={styles.field}>
                                <span className={styles.fieldLabel}>Role</span>
                                <span className={`badge badge-primary ${styles.roleBadge}`}>
                                    {user?.role || 'patient'}
                                </span>
                            </div>
                            <div className={styles.field}>
                                <span className={styles.fieldLabel}>Member Since</span>
                                <span className={styles.fieldValue}>
                                    {user?.created_at
                                        ? new Date(user.created_at).toLocaleDateString('en-US', {
                                            month: 'long', day: 'numeric', year: 'numeric',
                                        })
                                        : '—'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Data Management */}
                <div className={`card ${styles.dangerCard}`}>
                    <h2 className={styles.cardTitle}>🔒 Data & Privacy</h2>
                    <p className={styles.cardDesc}>
                        Manage your stored data. Deleting your reports and diagnoses is permanent and cannot be undone.
                    </p>
                    <div className={styles.dangerActions}>
                        <button
                            className="btn btn-outline"
                            onClick={() => router.push('/history')}
                        >
                            Manage Diagnoses →
                        </button>
                        <button
                            className="btn btn-danger"
                            onClick={logout}
                        >
                            Sign Out
                        </button>
                    </div>
                </div>

                {/* About */}
                <div className={`card ${styles.aboutCard}`}>
                    <h2 className={styles.cardTitle}>ℹ️ About Cura3.ai</h2>
                    <div className={styles.aboutInfo}>
                        <div className={styles.field}>
                            <span className={styles.fieldLabel}>Version</span>
                            <span className={styles.fieldValue}>2.0.0</span>
                        </div>
                        <div className={styles.field}>
                            <span className={styles.fieldLabel}>AI Model</span>
                            <span className={styles.fieldValue}>OpenAI GPT-4.1</span>
                        </div>
                        <div className={styles.field}>
                            <span className={styles.fieldLabel}>Specialists</span>
                            <span className={styles.fieldValue}>10+ Medical Specialists</span>
                        </div>
                    </div>
                    <div className={styles.aboutLinks}>
                        <a href="/terms" className="btn btn-ghost btn-sm">Terms of Service</a>
                        <a href="/privacy" className="btn btn-ghost btn-sm">Privacy Policy</a>
                        <a href="/disclaimer" className="btn btn-ghost btn-sm">Medical Disclaimer</a>
                    </div>
                </div>
            </main>
        </div>
    );
}
