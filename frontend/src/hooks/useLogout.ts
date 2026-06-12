'use client';

import { API_URL } from '@/constants';
import { useState, useCallback } from 'react';

export const useLogout = () => {
    const [isLoading, setIsLoading] = useState(false);

    const logout = useCallback(async () => {
        setIsLoading(true);

        try {
            await fetch(`${API_URL}/auth/logout`, {
                method: 'POST',
                credentials: 'include',
            });
        } catch (error) {
            // Si la llamada falla igual seguimos: el cliente se va al login.
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { logout, isLoading };
}
