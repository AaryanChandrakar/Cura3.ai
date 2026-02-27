'use client';

import React, { useState, useEffect } from 'react';
import styles from './CookieConsent.module.css';

const CONSENT_KEY = 'cura3_cookie_consent';

export default function CookieConsent() {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        // Show banner if consent hasn't been given yet
        const consent = localStorage.getItem(CONSENT_KEY);
        if (!consent) {
            // Small delay for a smoother entrance
            const timer = setTimeout(() => setVisible(true), 1500);
            return () => clearTimeout(timer);
        }
    }, []);

    const handleAccept = () => {
        localStorage.setItem(CONSENT_KEY, 'accepted');
        setVisible(false);
    };

    const handleDecline = () => {
        localStorage.setItem(CONSENT_KEY, 'declined');
        setVisible(false);
    };

    if (!visible) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.banner}>
                <div className={styles.content}>
                    <div className={styles.iconRow}>
                        <span className={styles.icon}>🍪</span>
                        <h3 className={styles.title}>Cookie Notice</h3>
                    </div>
                    <p className={styles.description}>
                        We use essential cookies to keep you signed in and ensure the platform works correctly.
                        We also use analytics cookies to understand how you use Cura3.ai so we can improve the experience.
                        No personal health information (PHI) is ever stored in cookies.
                    </p>
                    <p className={styles.links}>
                        Read our{' '}
                        <a href="/privacy" className={styles.link}>Privacy Policy</a>
                        {' '}and{' '}
                        <a href="/terms" className={styles.link}>Terms of Service</a>.
                    </p>
                </div>
                <div className={styles.actions}>
                    <button className={styles.declineBtn} onClick={handleDecline}>
                        Decline Optional
                    </button>
                    <button className={styles.acceptBtn} onClick={handleAccept}>
                        Accept All
                    </button>
                </div>
            </div>
        </div>
    );
}
