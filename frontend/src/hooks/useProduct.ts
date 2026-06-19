'use client';

import { API_URL } from '@/constants';
import { useEffect, useState, useCallback } from 'react';
import { Product } from '@/types/product';

export const useProducts = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchProducts = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/productos`, { cache: 'no-store' });
            if (!res.ok) throw new Error('Failed to fetch products');
            const data = await res.json();
            setProducts(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchProducts();
    }, [fetchProducts]);

    return { products, loading, refresh: fetchProducts };
}


export const useProduct = (id: number | string) => {
    const [product, setProduct] = useState<Product | undefined>(undefined);
    const [loading, setLoading] = useState(false);

    const getProduct = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/productos/${id}`, { cache: 'no-store' });
            if (!res.ok) throw new Error('Failed to fetch product');
            const data = await res.json();
            setProduct(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        getProduct();
    }, [getProduct]);

    return { product, loading };
}  