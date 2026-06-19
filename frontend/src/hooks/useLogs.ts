'use client';

import { useEffect, useState } from 'react';
import {API_URL} from '@/constants';
import {EventoPorUsuario, EventoPorProducto} from '@/types/cassandra';

export const useLogEvent = (id_usuario: string, id_producto: number, evento: string) => {
    useEffect(() => {
        const logEvent = async () => {
            await fetch(`${API_URL}/cassandra/evento`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_usuario: parseInt(id_usuario), id_producto, evento }),
            });
        };
        logEvent();
    }, [id_usuario, id_producto, evento]);
}

export const useGetProductFunnel = (id_producto: string | number, evento: string) => {
    const [funnelData, setFunnelData] = useState<EventoPorProducto[]>([]);

    useEffect(() => {
        const fetchFunnelData = async () => {
            const res = await fetch(`${API_URL}/producto/${id_producto}/embudo?evento=${evento}`, { cache: 'no-store' });
            if (!res.ok) return;
            const data = await res.json();
            setFunnelData(data);
        };
        fetchFunnelData();
    }, [id_producto, evento]);

    return funnelData;
};