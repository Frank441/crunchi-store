'use client';

import { useState, useCallback } from 'react';

type LoginFields = {
    email: string;
    password: string;
}

export const useLogin = () => {
    const [errors, setErrors] = useState<string | null | LoginFields>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const login = useCallback(async (email: string, password: string) => {
        setIsLoading(true);
        setErrors(null);
        
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                setErrors(errorData.message || 'Login failed');
            } else {
                setIsLoggedIn(true);
            }
        } catch (error) {
            setErrors('An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);
    
    return { login, errors, isLoading, isLoggedIn };
}