'use client';
import { useState } from 'react';
import { EventoPorProducto } from '@/types/cassandra';
import { Product } from '@/types/product';
// IMPORTACIÓN CORREGIDA: Traemos la función que usa tu API_URL real sin el /api/ intruso
import { getProductFunnel } from '@/lib/events/logEvent';

interface ProductFunnelProps {
  productos: Product[];
}

const EVENTOS_FILTRO = [
  "HOME_PAGE_VISIT", 
  "SEARCH", 
  "VIEW_PRODUCT", 
  "ADD_TO_CART",
  "REMOVE_FROM_CART", 
  "CHECKOUT_START", 
  "PURCHASE_COMPLETE",
  "LEAVE_REVIEW", 
  "ADD_TO_WISHLIST"
];

export default function ProductFunnel({ productos }: ProductFunnelProps) {
  const [selectedProduct, setSelectedProduct] = useState<string>(productos[0]?.id?.toString() ?? '');
  const [selectedEvento, setSelectedEvento] = useState<string>('VIEW_PRODUCT');
  const [logs, setLogs] = useState<EventoPorProducto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchFunnel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct) return;

    setLoading(true);
    setError(null);

    try {
      // LLAMADA CORREGIDA: Consumimos la función centralizada del wrapper
      const data = await getProductFunnel(selectedProduct, selectedEvento);
      setLogs(data);
      
      if (data.length === 0) {
        setError('No se registraron interacciones para este evento en el producto seleccionado.');
      }
    } catch (err) {
      setError('No se pudo conectar con el clúster de Cassandra.');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 w-full">
      <div className="mb-6">
        <h2 className="text-xl font-extrabold font-ubuntu text-white flex items-center gap-2">
          <span>📊</span> Embudo de Conversión por Producto
        </h2>
        <p className="text-xs font-inter text-white/40 mt-1">
          Métricas optimizadas para análisis.
        </p>
      </div>

      {/* Formulario de Filtros */}
      <form onSubmit={handleFetchFunnel} className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6 items-end font-inter">
        <div>
          <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Seleccionar Producto</label>
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2 rounded-xl focus:outline-none focus:border-primary/60 w-full"
          >
            {productos.map((p) => (
              <option key={p.id} value={p.id} className="bg-neutral-900">
                {p.nombre} ({p.categoria})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Filtrar Etapa (Evento)</label>
          <select
            value={selectedEvento}
            onChange={(e) => setSelectedEvento(e.target.value)}
            className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2 rounded-xl focus:outline-none focus:border-primary/60 w-full"
          >
            {EVENTOS_FILTRO.map((ev) => (
              <option key={ev} value={ev} className="bg-neutral-900">
                {ev}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="bg-white/10 hover:bg-primary hover:text-black text-white font-ubuntu font-bold h-10 rounded-xl transition-all duration-300 cursor-pointer text-sm"
        >
          {loading ? 'Analizando...' : 'Consultar'}
        </button>
      </form>

      {error && <p className="text-amber-400/90 font-inter text-xs mb-4 bg-amber-500/5 border border-amber-500/10 p-3 rounded-xl">{error}</p>}

      {/* Métrica Rápida de Volumen de Conversión */}
      {logs.length > 0 && (
        <div className="mb-4 bg-primary/10 border border-primary/20 rounded-xl p-4 font-inter">
          <p className="text-xs text-white/60 uppercase font-bold tracking-wider">Conversiones Totales Detectadas</p>
          <p className="text-3xl font-extrabold text-primary font-ubuntu mt-1">
            {logs.length} <span className="text-sm font-normal text-white/40">hits en esta partición</span>
          </p>
        </div>
      )}

      {/* Tabla de Eventos de la Partición */}
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-left border-collapse font-inter text-sm">
          <thead>
            <tr className="bg-white/5 text-white/60 border-b border-white/10 text-xs uppercase tracking-wider">
              <th className="p-4 font-semibold">Usuario Interactuante</th>
              <th className="p-4 font-semibold">Fecha y Hora</th>
              <th className="p-4 font-semibold font-mono text-white/30">TimeUUID (Clustering DESC)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-white/80">
            {logs.length > 0 ? (
              logs.map((item) => (
                <tr key={item.id_evento} className="hover:bg-white/5 transition-colors duration-200">
                  <td className="p-4 font-medium text-white/90">
                    <span className="bg-white/5 px-2 py-1 rounded-md text-xs font-mono text-primary border border-white/5">
                      👤 {item.id_usuario}
                    </span>
                  </td>
                  <td className="p-4 text-white/60">{new Date(item.fecha_hora).toLocaleString('es-AR')}</td>
                  <td className="p-4 font-mono text-xs text-white/30 max-w-[120px] truncate">{item.id_evento}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="p-8 text-center text-white/40 italic">
                  Seleccioná un producto y un evento para auditar los registros físicos de Cassandra.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}