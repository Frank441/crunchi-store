import Image from 'next/image';
import { Product } from '@/types/product';

const formatearPrecio = (precio: number) =>
    new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        maximumFractionDigits: 0,
    }).format(precio);

const ProductCard = ({ producto }: { producto: Product }) => {
    const imagen = producto.imagenes[0] ?? '/logo.png';

    return (
        <article className="shrink-0 w-52 bg-white/5 rounded-2xl overflow-hidden border border-white/10 transition-all duration-300 hover:border-primary/60 hover:-translate-y-1">
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
        </article>
    );
};

export default ProductCard;
