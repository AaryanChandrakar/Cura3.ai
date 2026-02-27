'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import styles from './Sidebar.module.css';

const NAV_ITEMS = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/analyze', label: 'New Diagnosis', icon: '🔬' },
    { href: '/history', label: 'History', icon: '📋' },
    { href: '/chat', label: 'Chat', icon: '💬' },
    { href: '/settings', label: 'Settings', icon: '⚙️' },
];

const ADMIN_ITEMS = [
    { href: '/admin', label: 'Admin Panel', icon: '🛡️' },
    { href: '/admin/analytics', label: 'Analytics', icon: '📈' },
];

export default function Sidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    return (
        <aside className={styles.sidebar}>
            {/* Logo */}
            <div className={styles.logo}>
                <Link href="/dashboard" className={styles.logoLink}>
                    <span className={styles.logoIcon}>🏥</span>
                    <span className={styles.logoText}>Cura3.ai</span>
                </Link>
                <span className={styles.logoBadge}>v2.0</span>
            </div>

            {/* Main Nav */}
            <nav className={styles.nav}>
                <div className={styles.navSection}>
                    <span className={styles.navLabel}>Main Menu</span>
                    {NAV_ITEMS.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`${styles.navItem} ${pathname === item.href ? styles.active : ''}`}
                        >
                            <span className={styles.navIcon}>{item.icon}</span>
                            <span>{item.label}</span>
                            {pathname === item.href && <span className={styles.activeIndicator} />}
                        </Link>
                    ))}
                </div>

                {/* Admin Section */}
                {user?.role === 'admin' && (
                    <div className={styles.navSection}>
                        <span className={styles.navLabel}>Administration</span>
                        {ADMIN_ITEMS.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`${styles.navItem} ${pathname === item.href ? styles.active : ''}`}
                            >
                                <span className={styles.navIcon}>{item.icon}</span>
                                <span>{item.label}</span>
                            </Link>
                        ))}
                    </div>
                )}
            </nav>

            {/* User Section */}
            <div className={styles.userSection}>
                <div className={styles.userInfo}>
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
                    <div className={styles.userMeta}>
                        <span className={styles.userName}>{user?.name || 'User'}</span>
                        <span className={styles.userRole}>{user?.role || 'patient'}</span>
                    </div>
                </div>
                <button onClick={logout} className={styles.logoutBtn} title="Sign out">
                    ↩
                </button>
            </div>
        </aside>
    );
}
