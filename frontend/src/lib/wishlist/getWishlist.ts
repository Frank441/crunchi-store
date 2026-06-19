import { API_URL } from '@/constants';
import { sessionCookieHeader } from '@/lib/auth/sessionHeader';
import { Product } from '@/types/product';

export interface Wishlist {
    productos: Product[];
    cantidad: number;
}

export async function getWishlist(): Promise<Wishlist> {
    const headers = await sessionCookieHeader();
    if (!headers) return { productos: [], cantidad: 0 };

    const res = await fetch(`${API_URL}/favoritos`, { headers, cache: 'no-store' });
    if (!res.ok) return { productos: [], cantidad: 0 };

    return res.json();
}

/** Solo los ids — para pintar el estado de los corazones en el catálogo. */
export async function getWishlistIds(): Promise<number[]> {
    const headers = await sessionCookieHeader();
    if (!headers) return [];

    const res = await fetch(`${API_URL}/favoritos/ids`, { headers, cache: 'no-store' });
    if (!res.ok) return [];

    return res.json();
}
