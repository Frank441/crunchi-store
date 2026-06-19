import { API_URL } from '@/constants';
import { EventoPorUsuario, EventoPorProducto } from '@/types/cassandra';

export async function logEvent(id_usuario: string, id_producto: number, evento: string) {
    const res = await fetch(`${API_URL}/cassandra/evento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            id_usuario: id_usuario,
            id_producto: id_producto,
            evento: evento,
            fecha_hora: new Date().toISOString() // <-- Agregamos la fecha explícita para evitar el 422 si es requerida
        }),
    });

    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        console.error("Error devuelto por FastAPI:", errorData);
        throw new Error('Error en los parámetros enviados al servidor.');
    }

    return res.json();
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