import { redirect } from 'next/navigation';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { getCart } from '@/lib/cart/getCart';
import CartView from './CartView';

export default async function CarritoPage() {
    const user = await getSessionUser();
    if (!user) redirect('/login');

    const carrito = await getCart();

    return (
        <div className="min-h-screen bg-background px-8 pb-16 pt-28">
            <div className="max-w-5xl mx-auto">
                <h1 className="text-4xl font-extrabold font-ubuntu text-white mb-10">Tu carrito</h1>
                <CartView inicial={carrito} />
            </div>
        </div>
    );
}
