import { API_URL } from '@/constants';
import { notifyStoreChanged } from '@/lib/store/notify';

export async function addFavorite(producto_id: number): Promise<void> {
    const res = await fetch(`${API_URL}/favoritos/${producto_id}`, {
        method: 'POST',
        credentials: 'include',
    });
    if (!res.ok) throw new Error('No se pudo agregar a favoritos');
    notifyStoreChanged();
}

export async function removeFavorite(producto_id: number): Promise<void> {
    const res = await fetch(`${API_URL}/favoritos/${producto_id}`, {
        method: 'DELETE',
        credentials: 'include',
    });
    if (!res.ok) throw new Error('No se pudo quitar de favoritos');
    notifyStoreChanged();
}

/** Devuelve el nuevo estado (true = quedó como favorito). */
export async function toggleFavorite(producto_id: number, eraFavorito: boolean): Promise<boolean> {
    if (eraFavorito) {
        await removeFavorite(producto_id);
        return false;
    }
    await addFavorite(producto_id);
    return true;
}
