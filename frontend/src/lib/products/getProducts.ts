import { API_URL } from '@/constants';
import { Product } from '@/types/product';

export async function getProducts(): Promise<Product[]> {
    const res = await fetch(`${API_URL}/productos`, { cache: 'no-store' });

    if (!res.ok) return [];

    return res.json();
}

export async function getProduct(id: number | string): Promise<Product | null> {
    const res = await fetch(`${API_URL}/productos/${id}`, { cache: 'no-store' });

    if (!res.ok) return null;

    return res.json();
}

/** Agrupa los productos por categoría preservando el orden de aparición. */
export function groupByCategory(products: Product[]): Record<string, Product[]> {
    return products.reduce<Record<string, Product[]>>((grupos, producto) => {
        (grupos[producto.categoria] ??= []).push(producto);
        return grupos;
    }, {});
}
