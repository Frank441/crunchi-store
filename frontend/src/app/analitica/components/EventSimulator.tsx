'use client';
import { useState } from 'react';
import { Product } from '@/types/product';
import { logEvent } from '@/lib/events/logEvent';

interface EventSimulatorProps {
  productos: Product[];
}

const EVENTOS_DISPONIBLES = [
  'VIEW_PRODUCT', 
  'ADD_TO_CART', 
  'REMOVE_FROM_CART', 
  'CHECKOUT_START', 
  'PURCHASE_COMPLETE'
];

export default function EventSimulator({ productos }: EventSimulatorProps) {
  const [isOpen, setIsOpen] = useState(false); // Estado para ocultar/mostrar
  const [selectedProduct, setSelectedProduct] = useState<string>(productos[0]?.id?.toString() ?? '');
  const [selectedEvento, setSelectedEvento] = useState<string>('VIEW_PRODUCT');
  const [customUserId, setCustomUserId] = useState<string>('999'); // ID por defecto local
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct || !customUserId) return;

    setLoading(true);
    setStatus(null);

    try {
      await logEvent(customUserId, parseInt(selectedProduct), selectedEvento);
      setStatus({
        type: 'success',
        message: `¡Evento ${selectedEvento} inyectado con éxito para el Usuario ${customUserId}!`
      });
      setTimeout(() => setStatus(null), 4000);
    } catch (err) {
      setStatus({
        type: 'error',
        message: 'No se pudo registrar el evento en el clúster.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 lg:col-span-2 transition-all duration-300">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-extrabold font-ubuntu text-white flex items-center gap-2">
            <span>🚀</span> Herramientas de Desarrollo
          </h2>
          <p className="text-xs font-inter text-white/40 mt-1">
            Simulador opcional para generar comportamientos calientes de compra en Cassandra.
          </p>
        </div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-xs font-ubuntu font-bold bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-xl cursor-pointer transition-all duration-200"
        >
          {isOpen ? 'Ocultar Simulador ✕' : 'Mostrar Simulador 🛠️'}
        </button>
      </div>

      {isOpen && (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end font-inter mt-6 pt-6 border-t border-white/5 dynamic-fade">
          <div>
            <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">ID Usuario</label>
            <input
              type="number"
              value={customUserId}
              onChange={(e) => setCustomUserId(e.target.value)}
              className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-primary/60 w-full"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Producto destino</label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-primary/60 w-full"
            >
              {productos.map((p) => (
                <option key={p.id} value={p.id} className="bg-neutral-900">
                  {p.nombre} ({p.categoria})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-white/50 uppercase tracking-wide mb-2">Acción a simular</label>
            <select
              value={selectedEvento}
              onChange={(e) => setSelectedEvento(e.target.value)}
              className="bg-black/20 border border-white/10 text-sm text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-primary/60 w-full"
            >
              {EVENTOS_DISPONIBLES.map((ev) => (
                <option key={ev} value={ev} className="bg-neutral-900">
                  {ev}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading || productos.length === 0}
            className="bg-primary hover:bg-primary/80 disabled:bg-white/10 disabled:text-white/40 text-black font-ubuntu font-bold h-10.5 rounded-xl transition-all duration-300 cursor-pointer text-sm w-full"
          >
            {loading ? 'Inyectando...' : 'Enviar Evento'}
          </button>
        </form>
      )}

      {status && isOpen && (
        <div className={`mt-4 p-3 rounded-xl text-xs font-inter border ${
          status.type === 'success' 
            ? 'bg-green-500/10 border-green-500/20 text-green-400' 
            : 'bg-red-500/10 border-red-500/20 text-red-400'
        }`}>
          {status.message}
        </div>
      )}
    </div>
  );
}