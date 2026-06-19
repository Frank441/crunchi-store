'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useLogout } from '@/hooks/useLogout';
import { API_URL } from '@/constants';
import { STORE_CHANGED_EVENT } from '@/lib/store/notify';
import ProductSearch from './ProductSearch';

const Header = ({ isAuthenticated }: { isAuthenticated: boolean }) => {
    const { push, refresh } = useRouter();
    const pathName = usePathname();
    const { logout, isLoading } = useLogout();

    const [cartCount, setCartCount] = useState(0);
    const [favCount, setFavCount] = useState(0);

    const refrescarContadores = useCallback(async () => {
        if (!isAuthenticated) return;
        try {
            const [carrito, favs] = await Promise.all([
                fetch(`${API_URL}/carrito`, { credentials: 'include', cache: 'no-store' }).then((r) => (r.ok ? r.json() : null)),
                fetch(`${API_URL}/favoritos/ids`, { credentials: 'include', cache: 'no-store' }).then((r) => (r.ok ? r.json() : [])),
            ]);
            setCartCount(carrito?.cantidad_items ?? 0);
            setFavCount(Array.isArray(favs) ? favs.length : 0);
        } catch {
            // Si falla, dejamos los contadores como están.
        }
    }, [isAuthenticated]);

    // Recargamos al montar, al navegar y cuando una acción dispara el evento del store.
    useEffect(() => {
        refrescarContadores();
        window.addEventListener(STORE_CHANGED_EVENT, refrescarContadores);
        return () => window.removeEventListener(STORE_CHANGED_EVENT, refrescarContadores);
    }, [refrescarContadores, pathName]);

    const goToLogin = () => push('/login');

    const handleLogout = async () => {
        await logout();
        // refresh re-renderiza el layout (server) para que el header refleje que ya no hay sesión.
        refresh();
        push('/login');
    };

    // Los CTA de marketing (Acceder / Explorar) solo en la landing pública para visitantes anónimos.
    const showMarketing = !isAuthenticated && pathName === '/';

    return (
        <header className="w-full bg-background/70 py-4 fixed z-100 top-0 px-8" suppressHydrationWarning>
            <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
                <Link href={isAuthenticated ? '/home' : '/'} className="flex items-center gap-2 shrink-0">
                    <Image src="/logo.png" alt="CrunchiStore Logo" width={50} height={50} className="w-6 h-6" />
                    <h1 className="text-lg font-bold text-primary font-ubuntu">CrunchiStore</h1>
                </Link>

                {isAuthenticated && (
                    <div className="flex-1 flex justify-center px-4">
                        <ProductSearch />
                    </div>
                )}

                {isAuthenticated ? (
                    <div className="flex items-center gap-3 shrink-0 -mr-4">
                        <IconoNav href="/favoritos" label="Favoritos" count={favCount}>
                            <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2}>
                                <path d="M12 21s-6.7-4.35-9.33-8.07C.9 10.27 1.6 6.8 4.5 5.6c1.96-.8 4.06-.1 5.2 1.5l.3.43.3-.43c1.14-1.6 3.24-2.3 5.2-1.5 2.9 1.2 3.6 4.67 1.83 7.33C18.7 16.65 12 21 12 21z" />
                            </svg>
                        </IconoNav>
                        <IconoNav href="/carrito" label="Carrito" count={cartCount}>
                            <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2}>
                                <circle cx="9" cy="21" r="1" />
                                <circle cx="20" cy="21" r="1" />
                                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                            </svg>
                        </IconoNav>
                        <button
                            onClick={handleLogout}
                            disabled={isLoading}
                            className="bg-black text-[14px] text-white uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed font-semibold font-helvetica tracking-widest"
                        >
                            {isLoading ? 'Saliendo...' : 'Cerrar sesión'}
                        </button>
                    </div>
                ) : showMarketing ? (
                    <div className="flex items-center gap-4 shrink-0">
                        <button onClick={goToLogin} className="bg-black text-[14px] text-white uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 hover:bg-gray-900 font-semibold font-helvetica tracking-widest">Acceder</button>
                        <button className="bg-transparent text-[14px] border-2 border-white/70 text-white/70 font-helvetica font-semibold uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 tracking-widest hover:text-white hover:border-white line-clamp-3">Explorar</button>
                    </div>
                ) : null}
            </div>
        </header>
    );
};

const IconoNav = ({ href, label, count, children }: { href: string; label: string; count: number; children: React.ReactNode }) => (
    <Link
        href={href}
        aria-label={`${label}${count > 0 ? ` (${count})` : ''}`}
        className="relative w-10 h-10 grid place-items-center rounded-full bg-white/10 text-white transition-colors duration-300 hover:bg-primary hover:text-black"
    >
        {children}
        {count > 0 && (
            <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 grid place-items-center rounded-full bg-primary text-black text-[11px] font-bold font-ubuntu">
                {count > 99 ? '99+' : count}
            </span>
        )}
    </Link>
);

export default Header;
