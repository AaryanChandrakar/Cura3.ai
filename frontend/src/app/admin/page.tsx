'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar/Sidebar';
import { listUsers, updateUserRole, getSystemStats, getAuditLogs, getApiUsage } from '@/lib/api';
import styles from './page.module.css';

// ── Types ────────────────────────────────────────────────

interface UserInfo {
    id: string;
    name: string;
    email: string;
    role: string;
    created_at: string;
    is_active: boolean;
}

interface SystemStats {
    users: { total: number; active: number; patients: number; doctors: number; admins: number };
    reports: { total: number };
    diagnoses: { total: number };
    chat_sessions: { total: number };
}

interface AuditLog {
    id: string;
    timestamp: string;
    method: string;
    path: string;
    status_code: number;
    duration_ms: number;
    client_ip: string;
    user_hint: string;
}

interface EndpointUsage {
    endpoint: string;
    total_requests: number;
    avg_duration_ms: number;
    min_duration_ms: number;
    max_duration_ms: number;
}

interface HourlyData {
    hour: string;
    requests: number;
}

// ── Mini Bar Chart (Canvas) ─────────────────────────────

function MiniBarChart({ data, width = 600, height = 200 }: { data: HourlyData[]; width?: number; height?: number }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || data.length === 0) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);

        // Clear
        ctx.clearRect(0, 0, width, height);

        const padding = { top: 20, right: 20, bottom: 40, left: 50 };
        const chartW = width - padding.left - padding.right;
        const chartH = height - padding.top - padding.bottom;

        const maxVal = Math.max(...data.map((d) => d.requests), 1);
        const barWidth = Math.max(2, (chartW / data.length) - 2);

        // Grid lines
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartH / 4) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();

            // Y-axis labels
            ctx.fillStyle = '#A0AEC0';
            ctx.font = '10px Inter, sans-serif';
            ctx.textAlign = 'right';
            const label = Math.round(maxVal * (1 - i / 4));
            ctx.fillText(String(label), padding.left - 8, y + 3);
        }

        // Bars with gradient
        data.forEach((d, i) => {
            const x = padding.left + (chartW / data.length) * i + 1;
            const barH = (d.requests / maxVal) * chartH;
            const y = padding.top + chartH - barH;

            const grad = ctx.createLinearGradient(x, y, x, y + barH);
            grad.addColorStop(0, '#0A6EBD');
            grad.addColorStop(1, '#12B886');
            ctx.fillStyle = grad;

            ctx.beginPath();
            ctx.roundRect(x, y, barWidth, barH, [3, 3, 0, 0]);
            ctx.fill();
        });

        // X-axis labels (every N-th)
        const labelEvery = Math.max(1, Math.floor(data.length / 6));
        ctx.fillStyle = '#A0AEC0';
        ctx.font = '9px Inter, sans-serif';
        ctx.textAlign = 'center';
        data.forEach((d, i) => {
            if (i % labelEvery === 0) {
                const x = padding.left + (chartW / data.length) * i + barWidth / 2;
                try {
                    const date = new Date(d.hour);
                    const label = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                    ctx.fillText(label, x, height - padding.bottom + 16);
                } catch { /* skip */ }
            }
        });
    }, [data, width, height]);

    if (data.length === 0) {
        return <div className={styles.chartEmpty}>No data available yet</div>;
    }

    return (
        <canvas
            ref={canvasRef}
            style={{ width, height, display: 'block' }}
        />
    );
}

// ── Method Badge ────────────────────────────────────────

function MethodBadge({ method }: { method: string }) {
    const colorMap: Record<string, string> = {
        GET: '#12B886',
        POST: '#0A6EBD',
        PUT: '#F59E0B',
        PATCH: '#8B5CF6',
        DELETE: '#E74C3C',
    };
    return (
        <span
            className={styles.methodBadge}
            style={{ background: `${colorMap[method] || '#A0AEC0'}18`, color: colorMap[method] || '#A0AEC0' }}
        >
            {method}
        </span>
    );
}

function StatusBadge({ code }: { code: number }) {
    const color = code < 300 ? '#12B886' : code < 400 ? '#F59E0B' : code < 500 ? '#E74C3C' : '#8B5CF6';
    return (
        <span className={styles.statusBadge} style={{ background: `${color}18`, color }}>
            {code}
        </span>
    );
}

// ── Main Admin Component ────────────────────────────────

export default function AdminPage() {
    const { user, loading, isAuthenticated } = useAuth();
    const router = useRouter();

    const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'api-usage' | 'audit-logs'>('overview');
    const [pageLoading, setPageLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    // Overview data
    const [users, setUsers] = useState<UserInfo[]>([]);
    const [stats, setStats] = useState<SystemStats | null>(null);

    // API Usage data
    const [apiUsage, setApiUsage] = useState<{ endpoints: EndpointUsage[]; hourly_requests: HourlyData[]; total_requests: number } | null>(null);
    const [usageHours, setUsageHours] = useState(24);
    const [usageLoading, setUsageLoading] = useState(false);

    // Audit Logs data
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
    const [auditPage, setAuditPage] = useState(1);
    const [auditTotal, setAuditTotal] = useState(0);
    const [auditTotalPages, setAuditTotalPages] = useState(0);
    const [auditLoading, setAuditLoading] = useState(false);
    const [auditMethodFilter, setAuditMethodFilter] = useState('');
    const [auditPathFilter, setAuditPathFilter] = useState('');

    // ── Auth guard
    useEffect(() => {
        if (!loading && !isAuthenticated) router.push('/');
        if (!loading && isAuthenticated && user?.role !== 'admin') router.push('/dashboard');
    }, [loading, isAuthenticated, user, router]);

    // ── Load overview data
    useEffect(() => {
        if (isAuthenticated && user?.role === 'admin') {
            Promise.all([
                listUsers().catch(() => ({ users: [] })),
                getSystemStats().catch(() => null),
            ]).then(([usersRes, statsRes]) => {
                setUsers(usersRes.users || []);
                setStats(statsRes);
                setPageLoading(false);
            });
        }
    }, [isAuthenticated, user]);

    // ── Load API usage (effect handles fetch inline)
    useEffect(() => {
        if (activeTab !== 'api-usage') return;
        let cancelled = false;
        (async () => {
            setUsageLoading(true);
            try {
                const data = await getApiUsage(usageHours);
                if (!cancelled) setApiUsage(data);
            } catch { /* ignore */ }
            if (!cancelled) setUsageLoading(false);
        })();
        return () => { cancelled = true; };
    }, [activeTab, usageHours]);

    // ── Load audit logs (effect handles fetch inline)
    useEffect(() => {
        if (activeTab !== 'audit-logs') return;
        let cancelled = false;
        (async () => {
            setAuditLoading(true);
            try {
                const filters: { method?: string; path_contains?: string } = {};
                if (auditMethodFilter) filters.method = auditMethodFilter;
                if (auditPathFilter) filters.path_contains = auditPathFilter;
                const data = await getAuditLogs(auditPage, 30, filters);
                if (!cancelled) {
                    setAuditLogs(data.logs || []);
                    setAuditTotal(data.total || 0);
                    setAuditTotalPages(data.total_pages || 0);
                }
            } catch { /* ignore */ }
            if (!cancelled) setAuditLoading(false);
        })();
        return () => { cancelled = true; };
    }, [activeTab, auditPage, auditMethodFilter, auditPathFilter]);

    // ── User role change
    const handleRoleChange = async (userId: string, newRole: string) => {
        try {
            await updateUserRole(userId, newRole);
            setUsers((prev) =>
                prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
            );
        } catch { /* ignore */ }
    };

    const filteredUsers = users.filter(
        (u) =>
            u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            u.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading || !isAuthenticated || user?.role !== 'admin') {
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
                <h1 className="page-title">Admin Panel</h1>
                <p className="page-subtitle">Monitor platform health, manage users, and review security logs.</p>

                {/* Tabs */}
                <div className={styles.tabs}>
                    {(['overview', 'users', 'api-usage', 'audit-logs'] as const).map((tab) => (
                        <button
                            key={tab}
                            className={`${styles.tab} ${activeTab === tab ? styles.active : ''}`}
                            onClick={() => setActiveTab(tab)}
                        >
                            {tab === 'overview' && '📊 Overview'}
                            {tab === 'users' && '👥 Users'}
                            {tab === 'api-usage' && '📡 API Usage'}
                            {tab === 'audit-logs' && '🛡️ Audit Logs'}
                        </button>
                    ))}
                </div>

                {/* ═══ Overview Tab ═══ */}
                {activeTab === 'overview' && (
                    <div className={styles.overviewGrid}>
                        {[
                            { label: 'Total Users', value: stats?.users?.total ?? '—', icon: '👥', color: '#0A6EBD' },
                            { label: 'Active Users', value: stats?.users?.active ?? '—', icon: '🟢', color: '#10B981' },
                            { label: 'Total Reports', value: stats?.reports?.total ?? '—', icon: '📋', color: '#12B886' },
                            { label: 'Total Diagnoses', value: stats?.diagnoses?.total ?? '—', icon: '🔬', color: '#6C63FF' },
                            { label: 'Chat Sessions', value: stats?.chat_sessions?.total ?? '—', icon: '💬', color: '#F59E0B' },
                            { label: 'Doctors', value: stats?.users?.doctors ?? '—', icon: '🩺', color: '#8B5CF6' },
                        ].map((stat) => (
                            <div key={stat.label} className={`card ${styles.adminStat}`}>
                                <span className={styles.adminStatIcon}>{stat.icon}</span>
                                <div>
                                    <span className={styles.adminStatValue}>{stat.value}</span>
                                    <span className={styles.adminStatLabel}>{stat.label}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* ═══ Users Tab ═══ */}
                {activeTab === 'users' && (
                    <div>
                        <div className={styles.searchBar}>
                            <input
                                type="text"
                                className="input-field"
                                placeholder="🔍 Search users..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        {pageLoading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
                                <div className="spinner spinner-lg" />
                            </div>
                        ) : (
                            <div className={styles.usersTable}>
                                <div className={styles.tableHeader}>
                                    <span>User</span>
                                    <span>Email</span>
                                    <span>Role</span>
                                    <span>Joined</span>
                                </div>
                                {filteredUsers.map((u) => (
                                    <div key={u.id} className={styles.tableRow}>
                                        <span className={styles.userName}>
                                            {u.name || '—'}
                                            {!u.is_active && <span className="badge badge-danger" style={{ marginLeft: 8 }}>Inactive</span>}
                                        </span>
                                        <span className={styles.userEmail}>{u.email}</span>
                                        <span>
                                            <select
                                                className={styles.roleSelect}
                                                value={u.role}
                                                onChange={(e) => handleRoleChange(u.id, e.target.value)}
                                            >
                                                <option value="patient">Patient</option>
                                                <option value="doctor">Doctor</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                        </span>
                                        <span className={styles.userDate}>
                                            {u.created_at
                                                ? new Date(u.created_at).toLocaleDateString('en-US', {
                                                    month: 'short', day: 'numeric', year: 'numeric',
                                                })
                                                : '—'}
                                        </span>
                                    </div>
                                ))}
                                {filteredUsers.length === 0 && (
                                    <div style={{ textAlign: 'center', padding: 32, color: 'var(--color-text-muted)' }}>
                                        No users found.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* ═══ API Usage Tab ═══ */}
                {activeTab === 'api-usage' && (
                    <div className="fade-in">
                        {/* Time Range Selector */}
                        <div className={styles.filterRow}>
                            <span className={styles.filterLabel}>Time Range:</span>
                            {[6, 12, 24, 48, 168].map((h) => (
                                <button
                                    key={h}
                                    className={`${styles.filterChip} ${usageHours === h ? styles.filterChipActive : ''}`}
                                    onClick={() => setUsageHours(h)}
                                >
                                    {h < 24 ? `${h}h` : h === 24 ? '24h' : h === 48 ? '2d' : '7d'}
                                </button>
                            ))}
                        </div>

                        {usageLoading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
                                <div className="spinner spinner-lg" />
                            </div>
                        ) : apiUsage ? (
                            <>
                                {/* Summary Card */}
                                <div className={`card ${styles.usageSummary}`}>
                                    <div className={styles.usageSummaryItem}>
                                        <span className={styles.usageSummaryValue}>{apiUsage.total_requests.toLocaleString()}</span>
                                        <span className={styles.usageSummaryLabel}>Total Requests</span>
                                    </div>
                                    <div className={styles.usageSummaryItem}>
                                        <span className={styles.usageSummaryValue}>{apiUsage.endpoints.length}</span>
                                        <span className={styles.usageSummaryLabel}>Active Endpoints</span>
                                    </div>
                                    <div className={styles.usageSummaryItem}>
                                        <span className={styles.usageSummaryValue}>
                                            {apiUsage.endpoints.length > 0
                                                ? `${Math.round(
                                                    apiUsage.endpoints.reduce((a, e) => a + e.avg_duration_ms, 0) / apiUsage.endpoints.length
                                                )}ms`
                                                : '—'}
                                        </span>
                                        <span className={styles.usageSummaryLabel}>Avg Response Time</span>
                                    </div>
                                </div>

                                {/* Hourly Chart */}
                                <div className={`card ${styles.chartCard}`}>
                                    <h3 className={styles.chartTitle}>Requests per Hour</h3>
                                    <MiniBarChart data={apiUsage.hourly_requests} width={700} height={200} />
                                </div>

                                {/* Endpoints Table */}
                                <div className={`card ${styles.endpointsCard}`}>
                                    <h3 className={styles.chartTitle}>Top Endpoints</h3>
                                    <div className={styles.endpointTable}>
                                        <div className={styles.endpointHeader}>
                                            <span>Endpoint</span>
                                            <span>Requests</span>
                                            <span>Avg</span>
                                            <span>Min</span>
                                            <span>Max</span>
                                        </div>
                                        {apiUsage.endpoints.map((ep) => {
                                            const [method, ...pathParts] = ep.endpoint.split(' ');
                                            return (
                                                <div key={ep.endpoint} className={styles.endpointRow}>
                                                    <span className={styles.endpointName}>
                                                        <MethodBadge method={method} />
                                                        <code>{pathParts.join(' ')}</code>
                                                    </span>
                                                    <span className={styles.endpointCount}>{ep.total_requests.toLocaleString()}</span>
                                                    <span>{ep.avg_duration_ms}ms</span>
                                                    <span style={{ color: 'var(--color-success)' }}>{ep.min_duration_ms}ms</span>
                                                    <span style={{ color: ep.max_duration_ms > 1000 ? 'var(--color-danger)' : 'var(--color-text-muted)' }}>
                                                        {ep.max_duration_ms}ms
                                                    </span>
                                                </div>
                                            );
                                        })}
                                        {apiUsage.endpoints.length === 0 && (
                                            <div className={styles.chartEmpty}>No API usage data yet. Data appears after requests are made.</div>
                                        )}
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="empty-state">
                                <div className="empty-state-icon">📡</div>
                                <p>Could not load API usage data.</p>
                            </div>
                        )}
                    </div>
                )}

                {/* ═══ Audit Logs Tab ═══ */}
                {activeTab === 'audit-logs' && (
                    <div className="fade-in">
                        {/* Filters */}
                        <div className={styles.filterRow}>
                            <select
                                className={`input-field ${styles.filterSelect}`}
                                value={auditMethodFilter}
                                onChange={(e) => { setAuditMethodFilter(e.target.value); setAuditPage(1); }}
                            >
                                <option value="">All Methods</option>
                                <option value="GET">GET</option>
                                <option value="POST">POST</option>
                                <option value="PUT">PUT</option>
                                <option value="PATCH">PATCH</option>
                                <option value="DELETE">DELETE</option>
                            </select>
                            <input
                                type="text"
                                className={`input-field ${styles.filterInput}`}
                                placeholder="Filter by path..."
                                value={auditPathFilter}
                                onChange={(e) => { setAuditPathFilter(e.target.value); setAuditPage(1); }}
                            />
                            <span className={styles.auditCount}>
                                {auditTotal.toLocaleString()} entries
                            </span>
                        </div>

                        {auditLoading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
                                <div className="spinner spinner-lg" />
                            </div>
                        ) : (
                            <>
                                <div className={styles.auditTable}>
                                    <div className={styles.auditHeader}>
                                        <span>Time</span>
                                        <span>Method</span>
                                        <span>Path</span>
                                        <span>Status</span>
                                        <span>Duration</span>
                                        <span>IP</span>
                                    </div>
                                    {auditLogs.map((log) => (
                                        <div key={log.id} className={styles.auditRow}>
                                            <span className={styles.auditTime}>
                                                {new Date(log.timestamp).toLocaleString('en-US', {
                                                    month: 'short', day: 'numeric',
                                                    hour: '2-digit', minute: '2-digit', second: '2-digit',
                                                })}
                                            </span>
                                            <span><MethodBadge method={log.method} /></span>
                                            <span className={styles.auditPath}>{log.path}</span>
                                            <span><StatusBadge code={log.status_code} /></span>
                                            <span className={styles.auditDuration}>{log.duration_ms}ms</span>
                                            <span className={styles.auditIp}>{log.client_ip}</span>
                                        </div>
                                    ))}
                                    {auditLogs.length === 0 && (
                                        <div className={styles.chartEmpty}>No audit logs recorded yet.</div>
                                    )}
                                </div>

                                {/* Pagination */}
                                {auditTotalPages > 1 && (
                                    <div className={styles.pagination}>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            disabled={auditPage <= 1}
                                            onClick={() => setAuditPage((p) => p - 1)}
                                        >
                                            ← Previous
                                        </button>
                                        <span className={styles.paginationInfo}>
                                            Page {auditPage} of {auditTotalPages}
                                        </span>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            disabled={auditPage >= auditTotalPages}
                                            onClick={() => setAuditPage((p) => p + 1)}
                                        >
                                            Next →
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
