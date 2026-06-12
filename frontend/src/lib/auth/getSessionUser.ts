import { cookies } from 'next/headers';
import { API_URL } from '@/constants';

export async function getSessionUser() {
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
}