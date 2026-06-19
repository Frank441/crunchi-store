import Image from 'next/image';
import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { getProduct } from '@/lib/products/getProducts';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import { getWishlistIds } from '@/lib/wishlist/getWishlist';
import { logEvent } from '@/lib/events/logEvent';
import { BuyButton } from './components';
import FavoriteButton from '@/components/FavoriteButton';
import { EVENT_TYPES } from '@/constants/events';
import { API_URL } from '@/constants';

const formatearPrecio = (precio: number) =>
    new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        maximumFractionDigits: 0,
    }).format(precio);

export default async function ProductoDetallePage({ params }: { params: Promise<{ id: string }> }) {
    const user = await getSessionUser();
    if (!user) redirect('/login');

    const { id } = await params;
    const producto = await getProduct(id);
    if (!producto) notFound();

    await logEvent(user.id, producto.id, EVENT_TYPES.VIEW_PRODUCT);

    // Redis: cada visita suma 1 al ranking de trending (ZINCRBY). Best-effort.
    await fetch(`${API_URL}/trending/vista/${producto.id}`, { method: 'POST', cache: 'no-store' }).catch(() => {});

    const favIds = await getWishlistIds();
    const esFavorito = favIds.includes(producto.id);
    const imagen = producto.imagenes[0] ?? '/logo.png';

    return (
        <div className="min-h-screen bg-background px-8 pb-16 pt-28">
            <div className="max-w-5xl mx-auto">
                <Link
                    href="/home"
                    className="inline-flex items-center gap-2 text-white/60 hover:text-white font-inter text-sm mb-8 transition-colors"
                >
                    ‹ Volver al catálogo
                </Link>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div className="relative w-full h-[30vh] md:h-auto rounded-3xl overflow-hidden bg-white/5 border border-white/10">
                        <Image
                            src={imagen}
                            alt={producto.nombre}
                            fill
                            sizes="(max-width: 768px) 100vw, 50vw"
                            className="object-cover"
                            priority
                        />
                    </div>

                    <div className="flex flex-col">
                        <span className="text-primary font-helvetica text-xs uppercase tracking-widest mb-2">{producto.categoria}</span>
                        <h1 className="text-3xl md:text-4xl font-extrabold font-ubuntu text-white mb-1">{producto.nombre}</h1>
                        <p className="text-white/40 font-inter text-sm uppercase tracking-wide mb-6">{producto.marca}</p>

                        <p className="text-4xl font-bold font-ubuntu text-white mb-6">{formatearPrecio(producto.precio)}</p>

                        <p className="text-white/70 font-inter leading-relaxed mb-6">{producto.descripcion}</p>

                        <p className={`font-inter text-sm mb-8 ${producto.stock > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {producto.stock > 0 ? `${producto.stock} disponibles` : 'Sin stock'}
                        </p>

                        <div className="flex items-center gap-3">
                            <BuyButton producto={producto} />
                            <FavoriteButton
                                productoId={producto.id}
                                esFavorito={esFavorito}
                                className="w-14 h-14 shrink-0 border border-white/20 bg-white/5 hover:bg-white/10"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
