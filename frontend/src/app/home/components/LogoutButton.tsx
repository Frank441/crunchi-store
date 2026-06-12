'use client';
import { useRouter } from 'next/navigation';
import { useLogout } from '@/hooks/useLogout';

const LogoutButton = () => {
    const { logout, isLoading } = useLogout();
    const { push, refresh } = useRouter();

    const handleLogout = async () => {
        await logout();
        // refresh limpia el render cacheado del server component antes de salir.
        refresh();
        push('/login');
    };

    return (
        <button
            onClick={handleLogout}
            disabled={isLoading}
            className="bg-black text-[14px] text-white uppercase py-2 px-4 rounded-full cursor-pointer transition-all duration-300 hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed font-semibold font-helvetica tracking-widest"
        >
            {isLoading ? 'Saliendo...' : 'Cerrar sesión'}
        </button>
    );
};

export default LogoutButton;
