import { cookies } from 'next/headers';

/** Reenvía la cookie de sesión a la API desde un Server Component.
 * Devuelve null si no hay sesión (el llamador decide el fallback). */
export async function sessionCookieHeader(): Promise<{ Cookie: string } | null> {
    const token = (await cookies()).get('session_token')?.value;
    if (!token) return null;
    return { Cookie: `session_token=${token}` };
}
