'use client';

import { API_URL } from '@/constants';
import { useState, useCallback } from 'react';

export const useRegister = () => {
    const [errors, setErrors] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isRegistered, setIsRegistered] = useState(false);

    const register = useCallback(async (email: string, password: string, alias: string) => {
        setIsLoading(true);
        setErrors(null);

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email, password, alias })
            });

            if (!response.ok) {
                const errorData = await response.json();
                setErrors(typeof errorData.detail === 'string' ? errorData.detail : 'No se pudo completar el registro');
            } else {
                setIsRegistered(true);
            }
        } catch (error) {
            setErrors('An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { register, errors, isLoading, isRegistered };
}
