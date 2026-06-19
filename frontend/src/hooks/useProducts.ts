'use client';

import { use, useMemo } from 'react';
import { getProducts } from '@/lib/products/getProducts';
import { Product } from '@/types/product';

export const useProducts = () => {
    const productsPromise = useMemo(
        () =>
            getProducts().catch((error) => {
                console.error(error);
                return [] as Product[];
            }),
        [],
    );

    const products = use(productsPromise);

    return { products };
};