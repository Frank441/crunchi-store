import { cookies } from 'next/headers';
import { cache } from 'react';
import { API_URL } from '@/constants';

// cache() deduplica el fetch a /auth/me dentro de un mismo render: el layout y la
// página pueden pedir la sesión sin pegarle dos veces al backend.
export const getSessionUser = cache(async () => {
    const cookieStore = await cookies();
    const auth = cookieStore.get('session_token');

    if (!auth) return null;

    const res = await fetch(`${API_URL}/auth/me`, {
        headers: {
            Cookie: `session_token=${auth.value}`,
        },
        cache: 'no-store',
    });

    if (!res.ok) return null;

    // /auth/me devuelve el usuario plano: { id, email, alias, rol }.
    return await res.json();
});