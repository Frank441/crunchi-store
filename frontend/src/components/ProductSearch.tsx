'use client';
import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { API_URL } from '@/constants';
import { Product } from '@/types/product';

const formatearPrecio = (precio: number) =>
    new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        maximumFractionDigits: 0,
    }).format(precio);

const ProductSearch = () => {
    const [productos, setProductos] = useState<Product[]>([]);
    const [query, setQuery] = useState('');
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Traemos el catálogo una vez y filtramos en el cliente (dataset chico → búsqueda instantánea).
    useEffect(() => {
        let activo = true;
        fetch(`${API_URL}/productos`)
            .then((r) => (r.ok ? r.json() : []))
            .then((data) => { if (activo) setProductos(data); })
            .catch(() => {});
        return () => { activo = false; };
    }, []);

    // Cerrar el dropdown al hacer click afuera.
    useEffect(() => {
        const onClick = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', onClick);
        return () => document.removeEventListener('mousedown', onClick);
    }, []);

    const q = query.trim().toLowerCase();
    const resultados = q
        ? productos
            .filter((p) => p.nombre.toLowerCase().includes(q) || p.marca.toLowerCase().includes(q) || p.categoria.toLowerCase().includes(q))
            .slice(0, 6)
        : [];

    const cerrar = () => { setOpen(false); setQuery(''); };

    return (
        <div ref={containerRef} className="relative w-full max-w-md">
            <input
                type="text"
                value={query}
                onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
                onFocus={() => setOpen(true)}
                onKeyDown={(e) => { if (e.key === 'Escape') cerrar(); }}
                placeholder="Buscar productos..."
                className="w-full bg-white/10 text-white placeholder:text-white/40 text-sm rounded-full py-2 px-4 outline-none border border-transparent focus:border-primary/60 transition-colors font-inter"
            />

            {open && q && (
                <div className="absolute top-full mt-2 w-full bg-[#111] border border-white/10 rounded-2xl overflow-hidden shadow-xl z-50">
                    {resultados.length === 0 ? (
                        <p className="px-4 py-3 text-white/40 text-sm font-inter">Sin resultados para “{query}”.</p>
                    ) : (
                        resultados.map((p) => (
                            <Link
                                key={p.id}
                                href={`/productos/${p.id}`}
                                onClick={cerrar}
                                className="flex items-center gap-3 px-3 py-2 hover:bg-white/5 transition-colors"
                            >
                                <div className="relative w-10 h-10 shrink-0 rounded-lg overflow-hidden bg-black/40">
                                    <Image src={p.imagenes[0] ?? '/logo.png'} alt={p.nombre} fill sizes="40px" className="object-cover" />
                                </div>
                                <div className="min-w-0 flex-1">
                                    <p className="text-white text-sm font-inter truncate">{p.nombre}</p>
                                    <p className="text-white/40 text-xs font-inter">{p.categoria}</p>
                                </div>
                                <span className="text-primary text-sm font-ubuntu font-bold shrink-0">{formatearPrecio(p.precio)}</span>
                            </Link>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default ProductSearch;
