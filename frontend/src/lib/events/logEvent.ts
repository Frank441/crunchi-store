import { API_URL } from '@/constants';

export async function logEvent(id_usuario: string, id_producto: number, evento: string) {
    await fetch(`${API_URL}/cassandra/evento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_usuario: parseInt(id_usuario), id_producto, evento }),
    });
}