'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Carrito, CheckoutResult } from '@/types/cart';
import { setCartQty, removeFromCart, clearCart, checkout } from '@/lib/cart/cartClient';
import { API_URL } from '@/constants';

const formatearPrecio = (precio: number) =>
    new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(precio);

const CartView = ({ inicial, idUsuario }: { inicial: Carrito; idUsuario: string }) => {
    const [carrito, setCarrito] = useState<Carrito>(inicial);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [compra, setCompra] = useState<CheckoutResult | null>(null);

    const correr = async (accion: () => Promise<Carrito>) => {
        setBusy(true);
        setError(null);
        try {
            setCarrito(await accion());
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Error inesperado');
        } finally {
            setBusy(false);
        }
    };

    const cambiarCantidad = (id: number, nueva: number) => correr(() => setCartQty(id, Math.max(0, nueva)));
    const quitar = (id: number) => correr(() => removeFromCart(id));

    const vaciar = async () => {
        setBusy(true);
        try {
            await clearCart();
            setCarrito({ items: [], total: 0, cantidad_items: 0 });
        } finally {
            setBusy(false);
        }
    };

    const finalizar = async () => {
        setBusy(true);
        setError(null);

        const itemsAComprar = [...carrito.items];

        try {
            const res = await checkout();
            setCompra(res);
            setCarrito({ items: [], total: 0, cantidad_items: 0 });
            
            // --- TRACKING POLÍGLOTA CON CANTIDADES ---
            itemsAComprar.forEach(({ producto, cantidad }) => {
                
                // 1. Log a Cassandra: agregamos "cantidad" al JSON
                fetch(`${API_URL}/cassandra/evento`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        id_usuario: idUsuario,
                        id_producto: producto.id,
                        evento: "PURCHASE_COMPLETE",
                        cantidad: cantidad, // <-- Enviamos cuántos compró
                        fecha_hora: new Date().toISOString()
                    }),
                }).catch(err => console.error("Error Cassandra (PURCHASE_COMPLETE):", err));

                // 2. Log a Neo4j: sumamos la propiedad en la arista del grafo
                fetch(`${API_URL}/neo4j/accion-usuario`, { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id_usuario: idUsuario,
                        id_producto: producto.id,
                        accion: 'COMPRO',
                        cantidad: cantidad // <-- Mandamos las unidades a Neo4j
                    })
                }).catch(err => console.error("Error Neo4j (COMPRO):", err));
            });

        } catch (e) {
            setError(e instanceof Error ? e.message : 'No se pudo finalizar la compra');
        } finally {
            setBusy(false);
        }
    };

    if (compra) {
        return (
            <div className="max-w-xl mx-auto text-center bg-white/5 border border-white/10 rounded-3xl p-10">
                <div className="text-5xl mb-4">🎉</div>
                <h2 className="text-2xl font-extrabold font-ubuntu text-white mb-2">¡Compra confirmada!</h2>
                <p className="text-white/60 font-inter mb-1">
                    {compra.unidades} unidad/es · {compra.lineas} producto/s
                </p>
                <p className="text-primary font-ubuntu font-bold text-3xl mb-8">{formatearPrecio(compra.total)}</p>
                <Link
                    href="/home"
                    className="inline-block px-10 py-3 rounded-full font-extrabold font-ubuntu uppercase tracking-wide bg-primary text-black transition-all duration-300 hover:bg-primary-hovered"
                >
                    Seguir comprando
                </Link>
            </div>
        );
    }

    if (carrito.items.length === 0) {
        return (
            <div className="max-w-xl mx-auto text-center bg-white/5 border border-white/10 rounded-3xl p-12">
                <div className="text-5xl mb-4">🛒</div>
                <p className="text-white/60 font-inter mb-8">Tu carrito está vacío.</p>
                <Link
                    href="/home"
                    className="inline-block px-10 py-3 rounded-full font-extrabold font-ubuntu uppercase tracking-wide bg-primary text-black transition-all duration-300 hover:bg-primary-hovered"
                >
                    Explorar productos
                </Link>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Lista de ítems */}
            <div className="lg:col-span-2 flex flex-col gap-4">
                {carrito.items.map(({ producto, cantidad, subtotal }) => {
                    const imagen = producto.imagenes[0] ?? '/logo.png';
                    return (
                        <div
                            key={producto.id}
                            className="flex gap-4 items-center bg-white/5 border border-white/10 rounded-2xl p-4"
                        >
                            <div className="relative w-20 h-20 rounded-xl overflow-hidden bg-black/40 shrink-0">
                                <Image src={imagen} alt={producto.nombre} fill sizes="80px" className="object-cover" />
                            </div>

                            <div className="flex-1 min-w-0">
                                <Link href={`/productos/${producto.id}`} className="text-white font-inter font-semibold text-sm line-clamp-2 hover:text-primary transition-colors">
                                    {producto.nombre}
                                </Link>
                                <p className="text-primary font-ubuntu font-bold mt-1">{formatearPrecio(producto.precio)}</p>
                            </div>

                            {/* Stepper de cantidad */}
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => cambiarCantidad(producto.id, cantidad - 1)}
                                    disabled={busy}
                                    aria-label="Restar"
                                    className="w-8 h-8 rounded-full bg-white/10 text-white grid place-items-center cursor-pointer hover:bg-white/20 disabled:opacity-40"
                                >
                                    −
                                </button>
                                <span className="w-8 text-center text-white font-ubuntu font-bold">{cantidad}</span>
                                <button
                                    onClick={() => cambiarCantidad(producto.id, cantidad + 1)}
                                    disabled={busy || cantidad >= producto.stock}
                                    aria-label="Sumar"
                                    className="w-8 h-8 rounded-full bg-white/10 text-white grid place-items-center cursor-pointer hover:bg-white/20 disabled:opacity-40"
                                >
                                    +
                                </button>
                            </div>

                            <div className="w-28 text-right hidden sm:block">
                                <p className="text-white font-ubuntu font-bold">{formatearPrecio(subtotal)}</p>
                            </div>

                            <button
                                onClick={() => quitar(producto.id)}
                                disabled={busy}
                                aria-label="Quitar"
                                className="text-white/40 hover:text-red-400 transition-colors cursor-pointer text-xl px-2 disabled:opacity-40"
                            >
                                ×
                            </button>
                        </div>
                    );
                })}

                <button
                    onClick={vaciar}
                    disabled={busy}
                    className="self-start text-white/40 hover:text-red-400 text-sm font-inter transition-colors cursor-pointer mt-2 disabled:opacity-40"
                >
                    Vaciar carrito
                </button>
            </div>

            {/* Resumen */}
            <div className="bg-white/5 border border-white/10 rounded-3xl p-6 h-fit lg:sticky lg:top-28">
                <h2 className="text-xl font-extrabold font-ubuntu text-white mb-6">Resumen</h2>
                <div className="flex justify-between text-white/60 font-inter mb-2">
                    <span>Productos</span>
                    <span>{carrito.cantidad_items}</span>
                </div>
                <div className="flex justify-between text-white font-ubuntu font-bold text-2xl border-t border-white/10 pt-4 mb-6">
                    <span>Total</span>
                    <span>{formatearPrecio(carrito.total)}</span>
                </div>

                {error && <p className="text-red-400 text-sm font-inter mb-4">{error}</p>}

                <button
                    onClick={finalizar}
                    disabled={busy}
                    className="w-full px-8 py-4 rounded-full font-extrabold font-ubuntu uppercase tracking-wide bg-primary text-black transition-all duration-300 hover:bg-primary-hovered disabled:opacity-50 cursor-pointer"
                >
                    {busy ? 'Procesando...' : 'Finalizar compra'}
                </button>
            </div>
        </div>
    );
};

export default CartView;
