import { API_URL } from '@/constants';

/** Suma 1 vista al producto en el ranking (ZINCRBY). Best-effort: no rompe la UI si falla. */
export async function registrarVista(producto_id: number): Promise<void> {
    try {
        await fetch(`${API_URL}/trending/vista/${producto_id}`, { method: 'POST' });
    } catch {
        // El trending es secundario: si falla, la ficha del producto igual se muestra.
    }
}
