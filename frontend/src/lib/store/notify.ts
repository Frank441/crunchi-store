/** Evento de browser para avisar al Header que los contadores (carrito/favoritos)
 * cambiaron, sin necesidad de recargar la página. */
export const STORE_CHANGED_EVENT = 'crunchi:store-changed';

export function notifyStoreChanged() {
    if (typeof window !== 'undefined') {
        window.dispatchEvent(new Event(STORE_CHANGED_EVENT));
    }
}
