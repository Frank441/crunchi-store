'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toggleFavorite } from '@/lib/wishlist/wishlistClient';

interface FavoriteButtonProps {
    productoId: number;
    esFavorito: boolean;
    /** Si true, refresca la página (server) tras el cambio. Útil en /favoritos. */
    refreshOnChange?: boolean;
    className?: string;
}

const FavoriteButton = ({ productoId, esFavorito, refreshOnChange = false, className = '' }: FavoriteButtonProps) => {
    const [fav, setFav] = useState(esFavorito);
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleClick = async (e: React.MouseEvent) => {
        // El botón suele vivir dentro de un <Link>: evitamos navegar al togglear.
        e.preventDefault();
        e.stopPropagation();
        if (loading) return;

        const previo = fav;
        setLoading(true);
        setFav(!previo); // optimista

        try {
            const nuevo = await toggleFavorite(productoId, previo);
            setFav(nuevo);
            if (refreshOnChange) router.refresh();
        } catch {
            setFav(previo); // revertimos si falló
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleClick}
            disabled={loading}
            aria-label={fav ? 'Quitar de favoritos' : 'Agregar a favoritos'}
            aria-pressed={fav}
            className={`grid place-items-center rounded-full transition-all duration-200 cursor-pointer disabled:opacity-60 ${fav ? 'text-primary' : 'text-white/70 hover:text-white'} ${className}`}
        >
            <svg
                viewBox="0 0 24 24"
                className="w-5 h-5"
                fill={fav ? 'currentColor' : 'none'}
                stroke="currentColor"
                strokeWidth={2}
            >
                <path d="M12 21s-6.7-4.35-9.33-8.07C.9 10.27 1.6 6.8 4.5 5.6c1.96-.8 4.06-.1 5.2 1.5l.3.43.3-.43c1.14-1.6 3.24-2.3 5.2-1.5 2.9 1.2 3.6 4.67 1.83 7.33C18.7 16.65 12 21 12 21z" />
            </svg>
        </button>
    );
};

export default FavoriteButton;
