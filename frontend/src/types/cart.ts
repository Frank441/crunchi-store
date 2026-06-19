import { Product } from './product';

export interface CartItem {
    producto: Product;
    cantidad: number;
    subtotal: number;
}

export interface Carrito {
    items: CartItem[];
    total: number;
    cantidad_items: number;
}

export interface CheckoutResult {
    status: string;
    total: number;
    lineas: number;
    unidades: number;
    productos_comprados: number[];
}
