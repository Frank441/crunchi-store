'use client';

import { useState, useEffect, useMemo } from 'react';
import { useProducts } from '@/hooks';
import { groupByCategory } from '@/lib/products/getProducts';
import { CategoryCarousel } from './components';

// Orden en que mostramos las categorías (las no listadas van al final).
const ORDEN_CATEGORIAS = ['Figuras', 'Mangas', 'Indumentaria'];

type HomePageContentProps = {
    alias: string;
};

export default function PageContent({ alias }: HomePageContentProps) {
    const { products } = useProducts();
    // const [porCategoria, setPorCategoria] = useState();
    const [categorias, setCategorias] = useState<any>()

    // useEffect(() => {
    //     if (products?.length > 0) groupByCategory(products);
        const porCategoria = useMemo(() =>  groupByCategory(products), [products]);
    // },[products])

    // useEffect(() => {
    //     if (porCategoria) {
            
    //     }
    // }, [porCategoria])

    useEffect(()=>{
        setCategorias(Object.keys(porCategoria).sort((a, b) => {
                    const ia = ORDEN_CATEGORIAS.indexOf(a);
                    const ib = ORDEN_CATEGORIAS.indexOf(b);
                    return (ia === -1 ? Infinity : ia) - (ib === -1 ? Infinity : ib);
                }))
    }, [porCategoria])
    // const categorias = useMemo(
    //     () =>{
    //         if(Object.){

                
    //         }
    //     },
    //     [porCategoria],
    // );

    console.log(porCategoria)

    return (
        <div className="min-h-screen bg-background px-8 pb-8 pt-28">
            <div className="max-w-5xl mx-auto">
                <h1 className="text-4xl font-extrabold font-ubuntu mb-10">Hola, {alias}</h1>

                {categorias?.length === 0 ? (
                    <p className="text-lg text-gray-400 font-inter">No hay productos para mostrar.</p>
                ) : (
                    categorias?.map((categoria: any) => (
                        <CategoryCarousel
                            key={categoria}
                            titulo={categoria}
                            productos={porCategoria[categoria]}
                        />
                    ))
                )}
            </div>
        </div>
    );
}