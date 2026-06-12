'use client';
import { useRef } from 'react';
import { Product } from '@/types/product';
import ProductCard from './ProductCard';

interface CategoryCarouselProps {
    titulo: string;
    productos: Product[];
}

const CategoryCarousel = ({ titulo, productos }: CategoryCarouselProps) => {
    const trackRef = useRef<HTMLDivElement>(null);

    const scroll = (direccion: 'prev' | 'next') => {
        const track = trackRef.current;
        if (!track) return;
        // Desplazamos ~80% del ancho visible para dejar un producto de contexto.
        const offset = track.clientWidth * 0.8;
        track.scrollBy({ left: direccion === 'next' ? offset : -offset, behavior: 'smooth' });
    };

    if (productos.length === 0) return null;

    return (
        <section className="mb-12">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-extrabold font-ubuntu text-white">{titulo}</h2>
                <div className="flex gap-2">
                    <button
                        onClick={() => scroll('prev')}
                        aria-label="Anterior"
                        className="w-9 h-9 rounded-full bg-white/10 text-white flex items-center justify-center cursor-pointer transition-colors duration-300 hover:bg-primary hover:text-black"
                    >
                        ‹
                    </button>
                    <button
                        onClick={() => scroll('next')}
                        aria-label="Siguiente"
                        className="w-9 h-9 rounded-full bg-white/10 text-white flex items-center justify-center cursor-pointer transition-colors duration-300 hover:bg-primary hover:text-black"
                    >
                        ›
                    </button>
                </div>
            </div>
            <div
                ref={trackRef}
                className="flex gap-4 overflow-x-auto scroll-smooth pb-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            >
                {productos.map((producto) => (
                    <ProductCard key={producto.id} producto={producto} />
                ))}
            </div>
        </section>
    );
};

export default CategoryCarousel;
