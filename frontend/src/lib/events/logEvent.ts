import { API_URL } from '@/constants';
import { EventoPorUsuario, EventoPorProducto } from '@/types/cassandra';

export async function logEvent(id_usuario: string, id_producto: number, evento: string) {
    await fetch(`${API_URL}/cassandra/evento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_usuario: parseInt(id_usuario), id_producto, evento }),
    });
}

/** Obtiene el historial cronológico de un usuario en base a su ID */
export async function getUserJourney(id_usuario: string | number): Promise<EventoPorUsuario[]> {
    // Agregamos un query param de límite para que el backend no escupa toda la base de datos
    const res = await fetch(`${API_URL}/usuario/${id_usuario}/journey`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
}

/** Obtiene los usuarios que realizaron un determinado evento sobre un producto */
export async function getProductFunnel(id_producto: string | number, evento: string): Promise<EventoPorProducto[]> {
    const res = await fetch(`${API_URL}/producto/${id_producto}/embudo?evento=${evento}`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
}