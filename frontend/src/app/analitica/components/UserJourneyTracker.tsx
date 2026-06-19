'use client';
import { useState } from 'react';
import { EventoPorUsuario } from '@/types/cassandra';
import { Product } from '@/types/product';
import { getUserJourney } from '@/lib/events/logEvent';

interface UserJourneyTrackerProps {
  productos: Product[];
}

export default function UserJourneyTracker({ productos }: UserJourneyTrackerProps) {
  const [userId, setUserId] = useState<string>(''); 
  const [journey, setJourney] = useState<EventoPorUsuario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getUserJourney(userId); 
      if (data.length === 0) {
        setError('No se encontraron eventos o el usuario no existe.');
      }
      setJourney(data);
    } catch (err) {
      setError('Error al conectar con el servidor.');
      setJourney([]);
    } finally {
      setLoading(false);
    }
  };

  const getNombreProducto = (idProducto: number) => {
    const prod = productos.find((p) => p.id === idProducto);
    return prod ? prod.nombre : `Producto #${idProducto}`;
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 w-full">
      <div className="mb-6">
        <h2 className="text-xl font-extrabold font-ubuntu text-white flex items-center gap-2">
          <span>🎯</span> Rastreador de Usuarios (User Journey)
        </h2>
        <p className="text-xs font-inter text-white/40 mt-1">
          Auditoría cronológica.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 mb-6">
        <input
          type="text" 
          placeholder="ID de Usuario (Ej: USR-999 o 15)"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="bg-black/20 border border-white/10 font-inter text-sm text-white px-4 py-2 rounded-xl focus:outline-none focus:border-primary/60 w-full sm:w-64"
        />
        <button
          type="submit"
          className="bg-white/10 hover:bg-primary hover:text-black text-white font-ubuntu font-bold px-5 py-2 rounded-xl transition-all duration-300 cursor-pointer text-sm"
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {error && <p className="text-red-400 font-inter text-xs mb-4">{error}</p>}

      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-left border-collapse font-inter text-sm">
          <thead>
            <tr className="bg-white/5 text-white/60 border-b border-white/10 text-xs uppercase tracking-wider">
              <th className="p-4 font-semibold">Evento</th>
              <th className="p-4 font-semibold">Producto</th>
              <th className="p-4 font-semibold">Fecha y Hora</th>
              <th className="p-4 font-semibold font-mono text-white/30">TimeUUID (DESC)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-white/80">
            {journey.length > 0 ? (
              journey.map((item) => (
                <tr key={item.id_evento} className="hover:bg-white/5 transition-colors duration-200">
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded-md text-xs font-bold whitespace-nowrap ${
                      item.evento === 'PURCHASE_COMPLETE' ? 'bg-green-500/20 text-green-400' :
                      item.evento === 'CHECKOUT_START' ? 'bg-emerald-500/20 text-emerald-400' :
                      item.evento.includes('CART') ? 'bg-amber-500/20 text-amber-400' : 
                      item.evento === 'ADD_TO_WISHLIST' ? 'bg-pink-500/20 text-pink-400' :
                      item.evento === 'LEAVE_REVIEW' ? 'bg-purple-500/20 text-purple-400' :
                      item.evento === 'SEARCH' ? 'bg-sky-500/20 text-sky-400' :
                      'bg-primary/25 text-primary'
                    }`}>
                      {item.evento}
                    </span>
                  </td>
                  <td className="p-4 text-primary font-medium max-w-xs truncate" title={getNombreProducto(item.id_producto)}>
                    {getNombreProducto(item.id_producto)}
                  </td>
                  <td className="p-4 text-white/60">{new Date(item.fecha_hora).toLocaleString('es-AR')}</td>
                  <td className="p-4 font-mono text-xs text-white/30 max-w-[100px] truncate">{item.id_evento}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="p-8 text-center text-white/40 italic">
                  Ingresá un ID de usuario para mapear el flujo de interacciones.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}