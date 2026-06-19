import { API_URL } from '@/constants';
import { sessionCookieHeader } from '@/lib/auth/sessionHeader';
import { Carrito } from '@/types/cart';

const CARRITO_VACIO: Carrito = { items: [], total: 0, cantidad_items: 0 };

export async function getCart(): Promise<Carrito> {
    const headers = await sessionCookieHeader();
    if (!headers) return CARRITO_VACIO;

    const res = await fetch(`${API_URL}/carrito`, { headers, cache: 'no-store' });
    if (!res.ok) return CARRITO_VACIO;

    return res.json();
}
