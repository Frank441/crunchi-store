import { API_URL } from '@/constants';
import { TrendingItem } from '@/types/trending';

/** Ranking público de productos más vistos (Redis Sorted Set). */
export async function getTrending(limit = 10): Promise<TrendingItem[]> {
    const res = await fetch(`${API_URL}/trending?limit=${limit}`, { cache: 'no-store' });
    if (!res.ok) return [];

    return res.json();
}
