'use client';

import Image from 'next/image';
import { useRouter, usePathname } from 'next/navigation';
import { useLogout } from '@/hooks/useLogout';
import ProductSearch from './ProductSearch';

const Header = ({ isAuthenticated }: { isAuthenticated: boolean }) => {
    const { push, refresh } = useRouter();
    const pathName = usePathname();
    const { logout, isLoading } = useLogout();

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
                <div className="flex items-center gap-2 shrink-0">
                    <Image src="/logo.png" alt="CrunchiStore Logo" width={50} height={50} className="w-6 h-6" />
                    <h1 className="text-lg font-bold text-primary font-ubuntu">CrunchiStore</h1>
                </div>

                {isAuthenticated && (
                    <div className="flex-1 flex justify-center px-4">
                        <ProductSearch />
                    </div>
                )}

                {isAuthenticated ? (
                    <button
                        onClick={handleLogout}
                        disabled={isLoading}
                        className="-mr-4 shrink-0 bg-black text-[14px] text-white uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed font-semibold font-helvetica tracking-widest"
                    >
                        {isLoading ? 'Saliendo...' : 'Cerrar sesión'}
                    </button>
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

export default Header;
