'use client';
import { useState, useEffect } from 'react';
import { EventoPorProducto } from '@/types/cassandra';
import { Product } from '@/types/product';
import { getProductFunnel } from '@/lib/events/logEvent';

interface ProductFunnelProps {
  productos: Product[];
}

const EVENTOS_CASSANDRA = [
  'VIEW_PRODUCT', 'ADD_TO_CART', 'REMOVE_FROM_CART', 
  'CHECKOUT_START', 'PURCHASE_COMPLETE'
];

export default function ProductFunnel({ productos }: ProductFunnelProps) {
  const [selectedProduct, setSelectedProduct] = useState<string>(productos[0]?.id?.toString() ?? '');
  const [selectedEvento, setSelectedEvento] = useState<string>('ADD_TO_CART');
  const [funnelData, setFunnelData] = useState<EventoPorProducto[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedProduct) return;
    
    const fetchFunnel = async () => {
      setLoading(true);
      try {
        const data = await getProductFunnel(selectedProduct, selectedEvento);
        setFunnelData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchFunnel();
  }, [selectedProduct, selectedEvento]);

  const totalEventos = funnelData.length;
  const clientesUnicos = new Set(funnelData.map((f) => f.id_usuario)).size;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="mb-6">
        <h2 className="text-xl font-extrabold font-ubuntu text-white flex items-center gap-2">
          <span>📊</span> Embudo por Producto (Funnel)
        </h2>
        <p className="text-xs font-inter text-white/40 mt-1">
          Filtro exacto `((id_producto, evento), id_evento)` sobre clusters de Cassandra.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 font-inter">
        <div>
          <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Producto Real</label>
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-primary/60 w-full"
          >
            {productos.length === 0 ? (
              <option value="">No hay productos disponibles</option>
            ) : (
              productos.map((p) => (
                <option key={p.id} value={p.id} className="bg-neutral-900">
                  {p.nombre} ({p.categoria})
                </option>
              ))
            )}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Acción / Evento</label>
          <select
            value={selectedEvento}
            onChange={(e) => setSelectedEvento(e.target.value)}
            className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-primary/60 w-full"
          >
            {EVENTOS_CASSANDRA.map((ev) => (
              <option key={ev} value={ev} className="bg-neutral-900">
                {ev}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6 font-inter">
        <div className="bg-white/5 border border-white/5 p-4 rounded-xl">
          <span className="text-xs text-white/40 block">Total Ocurrencias</span>
          <span className="text-2xl font-bold font-ubuntu text-primary">{loading ? '...' : totalEventos}</span>
        </div>
        <div className="bg-white/5 border border-white/5 p-4 rounded-xl">
          <span className="text-xs text-white/40 block">Usuarios Únicos</span>
          <span className="text-2xl font-bold font-ubuntu text-white">{loading ? '...' : clientesUnicos}</span>
        </div>
      </div>

      <h3 className="text-xs font-bold text-white/40 font-inter uppercase tracking-wide mb-3">Últimas interacciones:</h3>
      <div className="max-h-60 overflow-y-auto space-y-2 pr-1 font-inter [scrollbar-width:thin]">
        {loading ? (
          <p className="text-white/40 text-center py-4 text-sm">Consultando nodos...</p>
        ) : funnelData.length > 0 ? (
          funnelData.map((item) => (
            <div key={item.id_evento} className="bg-white/5 border border-white/5 p-3 rounded-xl flex justify-between items-center text-sm">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs">
                  {item.id_usuario}
                </div>
                <span className="text-white font-medium">Usuario ID #{item.id_usuario}</span>
              </div>
              <span className="text-xs text-white/40">
                {new Date(item.fecha_hora).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))
        ) : (
          <p className="text-white/30 text-center py-4 text-sm italic">Sin registros para este filtro.</p>
        )}
      </div>
    </div>
  );
}