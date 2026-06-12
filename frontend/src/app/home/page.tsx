import { getSessionUser } from '@/lib/auth/getSessionUser';
import { getProducts, groupByCategory } from '@/lib/products/getProducts';
import { redirect } from 'next/navigation';
import { CategoryCarousel } from './components';

// Orden en que mostramos las categorías (las no listadas van al final).
const ORDEN_CATEGORIAS = ['Figuras', 'Mangas', 'Indumentaria'];

export default async function HomePage() {
  const user = await getSessionUser();

  if (!user) redirect('/login');

  const productos = await getProducts();
  const porCategoria = groupByCategory(productos);

  const categorias = Object.keys(porCategoria).sort((a, b) => {
    const ia = ORDEN_CATEGORIAS.indexOf(a);
    const ib = ORDEN_CATEGORIAS.indexOf(b);
    return (ia === -1 ? Infinity : ia) - (ib === -1 ? Infinity : ib);
  });

  return (
    <div className="min-h-screen bg-background px-8 pb-8 pt-28">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-extrabold font-ubuntu mb-10">Hola, {user.alias}</h1>

        {categorias.length === 0 ? (
          <p className="text-lg text-gray-400 font-inter">No hay productos para mostrar.</p>
        ) : (
          categorias.map((categoria) => (
            <CategoryCarousel
              key={categoria}
              titulo={categoria}
              productos={porCategoria[categoria]}
            />
          ))
        )}
      </div>
    </div>
  )
}
