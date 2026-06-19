'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Product } from '@/types/product';
import { addToCart } from '@/lib/cart/cartClient';

const BuyButton = ({ producto }: { producto: Product }) => {
    const tieneTalles = !!producto.talles && producto.talles.length > 0;
    const [talle, setTalle] = useState<string | null>(null);
    const [agregado, setAgregado] = useState(false);
    const [cargando, setCargando] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const sinStock = producto.stock <= 0;
    const faltaTalle = tieneTalles && !talle;
    const deshabilitado = sinStock || faltaTalle || cargando;

    const handleAgregar = async () => {
        if (deshabilitado) return;
        setCargando(true);
        setError(null);
        try {
            await addToCart(producto.id, 1);
            setAgregado(true);
        } catch (e) {
            setError(e instanceof Error ? e.message : 'No se pudo agregar al carrito');
        } finally {
            setCargando(false);
        }
    };

    return (
        <div className="flex flex-col gap-4">
            {tieneTalles && (
                <div>
                    <p className="text-white/60 text-sm font-inter mb-2 uppercase tracking-wide">Talle</p>
                    <div className="flex gap-2 flex-wrap">
                        {producto.talles!.map((t) => (
                            <button
                                key={t}
                                onClick={() => { setTalle(t); setAgregado(false); }}
                                className={`px-4 py-2 rounded-full border uppercase text-sm font-semibold transition-colors duration-200 cursor-pointer ${talle === t ? 'bg-primary text-black border-primary' : 'border-white/20 text-white/70 hover:border-white/60'}`}
                            >
                                {t}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <button
                onClick={handleAgregar}
                disabled={deshabilitado}
                className="w-full md:w-auto px-12 py-4 rounded-full font-extrabold font-ubuntu uppercase tracking-wide transition-all duration-300 bg-primary text-black cursor-pointer hover:bg-primary-hovered disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-primary"
            >
                {sinStock ? 'Sin stock' : cargando ? 'Agregando...' : agregado ? 'Agregado al carrito ✓' : 'Agregar al carrito'}
            </button>

            {agregado && !error && (
                <Link href="/carrito" className="text-primary hover:text-primary-hovered text-sm font-inter font-semibold transition-colors">
                    Ir al carrito ›
                </Link>
            )}

            {error && <p className="text-red-400 text-sm font-inter">{error}</p>}

            {faltaTalle && (
                <p className="text-white/40 text-sm font-inter">Elegí un talle para continuar.</p>
            )}
        </div>
    );
};

export default BuyButton;
