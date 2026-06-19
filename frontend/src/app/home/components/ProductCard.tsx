import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';
import FavoriteButton from '@/components/FavoriteButton';

const formatearPrecio = (precio: number) =>
    new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        maximumFractionDigits: 0,
    }).format(precio);

interface ProductCardProps {
    producto: Product;
    esFavorito?: boolean;
    /** En /favoritos queremos que al quitar el corazón se recargue la lista. */
    refreshFavorito?: boolean;
}

const ProductCard = ({ producto, esFavorito = false, refreshFavorito = false }: ProductCardProps) => {
    const imagen = producto.imagenes[0] ?? '/logo.png';

    return (
        <div className="relative shrink-0 w-52">
            <FavoriteButton
                productoId={producto.id}
                esFavorito={esFavorito}
                refreshOnChange={refreshFavorito}
                className="absolute top-2 right-2 z-10 w-9 h-9 bg-black/50 backdrop-blur-sm hover:bg-black/70"
            />
            <Link
                href={`/productos/${producto.id}`}
                className="block bg-white/5 rounded-2xl overflow-hidden border border-white/10 transition-all duration-300 hover:border-primary/60 hover:-translate-y-1"
            >
                <div className="relative w-full h-64 bg-black/40">
                    <Image
                        src={imagen}
                        alt={producto.nombre}
                        fill
                        sizes="208px"
                        className="object-cover"
                    />
                </div>
                <div className="p-4 flex flex-col gap-1">
                    <p className="text-white font-inter font-semibold text-sm line-clamp-2 min-h-10">{producto.nombre}</p>
                    <p className="text-white/40 font-inter text-xs uppercase tracking-wide">{producto.marca}</p>
                    <p className="text-primary font-ubuntu font-bold text-lg mt-1">{formatearPrecio(producto.precio)}</p>
                </div>
            </Link>
        </div>
    );
};

export default ProductCard;
