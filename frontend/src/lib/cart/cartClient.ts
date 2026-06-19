import { API_URL } from '@/constants';
import { Carrito, CheckoutResult } from '@/types/cart';
import { notifyStoreChanged } from '@/lib/store/notify';

const opciones = (body?: unknown): RequestInit => ({
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...(body ? { body: JSON.stringify(body) } : {}),
});

/** Suma `cantidad` (delta) del producto al carrito. Devuelve el carrito actualizado. */
export async function addToCart(producto_id: number, cantidad = 1): Promise<Carrito> {
    const res = await fetch(`${API_URL}/carrito/items`, opciones({ producto_id, cantidad }));
    if (!res.ok) throw new Error('No se pudo agregar al carrito');
    const carrito = await res.json();
    notifyStoreChanged();
    return carrito;
}

/** Fija la cantidad absoluta de un producto (0 lo elimina). */
export async function setCartQty(producto_id: number, cantidad: number): Promise<Carrito> {
    const res = await fetch(`${API_URL}/carrito/items/${producto_id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cantidad }),
    });
    if (!res.ok) throw new Error('No se pudo actualizar la cantidad');
    const carrito = await res.json();
    notifyStoreChanged();
    return carrito;
}

export async function removeFromCart(producto_id: number): Promise<Carrito> {
    const res = await fetch(`${API_URL}/carrito/items/${producto_id}`, {
        method: 'DELETE',
        credentials: 'include',
    });
    if (!res.ok) throw new Error('No se pudo quitar el producto');
    const carrito = await res.json();
    notifyStoreChanged();
    return carrito;
}

export async function clearCart(): Promise<void> {
    await fetch(`${API_URL}/carrito`, { method: 'DELETE', credentials: 'include' });
    notifyStoreChanged();
}

export async function checkout(): Promise<CheckoutResult> {
    const res = await fetch(`${API_URL}/carrito/checkout`, opciones());
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo finalizar la compra');
    }
    const resultado = await res.json();
    notifyStoreChanged();
    return resultado;
}
