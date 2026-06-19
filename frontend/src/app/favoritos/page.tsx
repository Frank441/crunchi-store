import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { getWishlist } from '@/lib/wishlist/getWishlist';
import { ProductCard } from '@/app/home/components';

export default async function FavoritosPage() {
    const user = await getSessionUser();
    if (!user) redirect('/login');

    const { productos } = await getWishlist();

    return (
        <div className="min-h-screen bg-background px-8 pb-16 pt-28">
            <div className="max-w-5xl mx-auto">
                <h1 className="text-4xl font-extrabold font-ubuntu text-white mb-10">Tus favoritos</h1>

                {productos.length === 0 ? (
                    <div className="max-w-xl mx-auto text-center bg-white/5 border border-white/10 rounded-3xl p-12">
                        <div className="text-5xl mb-4">♡</div>
                        <p className="text-white/60 font-inter mb-8">Todavía no marcaste ningún producto como favorito.</p>
                        <Link
                            href="/home"
                            className="inline-block px-10 py-3 rounded-full font-extrabold font-ubuntu uppercase tracking-wide bg-primary text-black transition-all duration-300 hover:bg-primary-hovered"
                        >
                            Explorar productos
                        </Link>
                    </div>
                ) : (
                    <div className="flex flex-wrap gap-4">
                        {productos.map((producto) => (
                            <ProductCard key={producto.id} producto={producto} esFavorito refreshFavorito />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
