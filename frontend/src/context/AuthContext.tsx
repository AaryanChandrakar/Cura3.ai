'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchCurrentUser, serverLogout } from '@/lib/api';

interface User {
    id: string;
    email: string;
    name: string;
    avatar_url?: string;
    role: string;
    is_active: boolean;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    isAuthenticated: boolean;
    login: () => void;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    isAuthenticated: false,
    login: () => { },
    logout: () => { },
    refreshUser: async () => { },
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = useCallback(async () => {
        try {
            const token = localStorage.getItem('cura3_token');
            if (!token) {
                setUser(null);
                setLoading(false);
                return;
            }
            const userData = await fetchCurrentUser();
            setUser(userData);
        } catch {
            localStorage.removeItem('cura3_token');
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshUser();
    }, [refreshUser]);

    const login = () => {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        window.location.href = `${apiUrl}/api/v1/auth/login`;
    };

    const logout = async () => {
        await serverLogout();
        localStorage.removeItem('cura3_token');
        setUser(null);
        window.location.href = '/';
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                isAuthenticated: !!user,
                login,
                logout,
                refreshUser,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
