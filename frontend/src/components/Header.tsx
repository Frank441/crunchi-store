'use client';

import Image from 'next/image';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

const Header = () => {
    const { push } = useRouter();
    const pathName = usePathname();
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const goToLogin = () => {
        push('/login')
    }

    const showButtons = isMounted && pathName !== "/login";

    return (
        <header className="w-full bg-background/70 py-4 fixed z-100 top-0.5 flex items-center justify-around" suppressHydrationWarning>
            <div className="flex items-center gap-2">
                <Image src="/logo.png" alt="CrunchiStore Logo" width={50} height={50} className="w-6 h-6" />
                <h1 className="text-lg font-bold text-primary font-ubuntu">CrunchiStore</h1>
            </div>
            {showButtons &&
                <div className="flex items-center gap-4">
                    <button onClick={() => push('/cart')} className="bg-transparent text-[14px] border-2 border-white/70 text-white/70 font-helvetica font-semibold uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 tracking-widest hover:text-white hover:border-white line-clamp-3">Carrito</button>
                    <button onClick={goToLogin} className="bg-black text-[14px] text-white uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 hover:bg-gray-900 font-semibold font-helvetica tracking-widest">Acceder</button>
                    <button className="bg-transparent text-[14px] border-2 border-white/70 text-white/70 font-helvetica font-semibold uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 tracking-widest hover:text-white hover:border-white line-clamp-3">Explorar</button>
                </div>
            }
        </header>
    )
}

export default Header;