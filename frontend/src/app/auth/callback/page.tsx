'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Suspense } from 'react';

function CallbackHandler() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { refreshUser } = useAuth();

    useEffect(() => {
        const token = searchParams.get('token');
        if (token) {
            localStorage.setItem('cura3_token', token);
            refreshUser().then(() => {
                router.push('/dashboard');
            });
        } else {
            router.push('/');
        }
    }, [searchParams, router, refreshUser]);

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100vh',
            gap: '1rem',
        }}>
            <div className="spinner spinner-lg" />
            <p style={{ color: 'var(--color-text-secondary)' }}>Signing you in...</p>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
            }}>
                <div className="spinner spinner-lg" />
            </div>
        }>
            <CallbackHandler />
        </Suspense>
    );
}
