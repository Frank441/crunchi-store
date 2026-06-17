'use client';
import { useState, useEffect } from 'react';
import { Product } from '@/types/product';
import { getProducts } from '@/lib/products/getProducts';
import UserJourneyTracker from './components/UserJourneyTracker';
import ProductFunnel from './components/ProductFunnel';
import EventSimulator from './components/EventSimulator';

export default function AnaliticaPage() {
  const [productosReales, setProductosReales] = useState<Product[]>([]);
  const [activeTab, setActiveTab] = useState<'journey' | 'funnel'>('journey');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function cargarCatalogo() {
      const prods = await getProducts();
      setProductosReales(prods);
      setLoading(false);
    }
    cargarCatalogo();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center text-white/50 font-inter">
        Cargando Panel de Analítica...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-8 pb-8 pt-28">
      <div className="max-w-7xl mx-auto">
        
        {/* Encabezado unificado */}
        <header className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/5 pb-6">
          <div>
            <h1 className="text-4xl font-extrabold font-ubuntu text-white">Panel de Analítica</h1>
            <p className="text-sm font-inter text-primary mt-1">Métricas en Tiempo Real (Cassandra)</p>
          </div>
        </header>

        {/* Sección del Simulador Opcional */}
        <div className="mb-8">
          <EventSimulator productos={productosReales} />
        </div>

        {/* Selector de Solapas (Tabs) Estilo Anime Marketplace */}
        <div className="flex border-b border-white/10 mb-6 gap-2 font-ubuntu">
          <button
            onClick={() => setActiveTab('journey')}
            className={`px-6 py-3 font-bold text-sm rounded-t-xl transition-all duration-300 cursor-pointer ${
              activeTab === 'journey'
                ? 'bg-white/5 text-primary border-t-2 border-primary border-x border-white/10'
                : 'text-white/40 hover:text-white/80'
            }`}
          >
            🎯 Rastreador de Usuarios
          </button>
          <button
            onClick={() => setActiveTab('funnel')}
            className={`px-6 py-3 font-bold text-sm rounded-t-xl transition-all duration-300 cursor-pointer ${
              activeTab === 'funnel'
                ? 'bg-white/5 text-primary border-t-2 border-primary border-x border-white/10'
                : 'text-white/40 hover:text-white/80'
            }`}
          >
            📊 Embudo por Producto
          </button>
        </div>

        {/* Bloques Operativos con Renderizado Condicional al 100% de Ancho */}
        <main className="w-full flex">
          {activeTab === 'journey' ? (
            <UserJourneyTracker productos={productosReales} />
          ) : (
            <ProductFunnel productos={productosReales} />
          )}
        </main>

      </div>
    </div>
  );
}