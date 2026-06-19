import { API_URL } from '@/constants';
import { Product } from '@/types/product';

export interface RecomendacionItem {
  id_producto: number;
  titulo: string;
  relevancia: number;
}

export interface SugerenciaHome {
  id_producto: number;
  titulo: string;
  puntos_afinidad: number;
}

/** 1. Filtrado Colaborativo Item-Based hidratado con la data completa de Mongo */
export async function getItemBasedRecommendations(productoId: number, todosLosProductos: Product[]): Promise<Product[]> {
  try {
    const res = await fetch(`${API_URL}/productos/${productoId}/recomendados`, { cache: 'no-store' });
    if (!res.ok) return [];
    
    const datosRaw: RecomendacionItem[] = await res.json();
    const idsRecomendados = datosRaw.map(item => item.id_producto);

    // Mapeamos e hidratamos en el orden exacto de relevancia que dictaminó el Grafo
    return idsRecomendados
      .map(id => todosLosProductos.find(p => p.id === id))
      .filter((p): p is Product => !!p);
  } catch (error) {
    console.error("Error consultando Neo4j Item-Based:", error);
    return [];
  }
}

/** 2. Filtrado Colaborativo de Home (Afinidad por Géneros) hidratado */
export async function getHomeSuggestions(usuarioId: string, todosLosProductos: Product[]): Promise<Product[]> {
  try {
    const res = await fetch(`${API_URL}/usuarios/${usuarioId}/home-sugerencias`, { cache: 'no-store' });
    if (!res.ok) return [];
    
    const datosRaw: SugerenciaHome[] = await res.json();
    const idsSugeridos = datosRaw.map(item => item.id_producto);

    // Mapeamos e hidratamos conservando el orden de afinidad de Neo4j
    return idsSugeridos
      .map(id => todosLosProductos.find(p => p.id === id))
      .filter((p): p is Product => !!p);
  } catch (error) {
    console.error("Error consultando Neo4j Home suggestions:", error);
    return [];
  }
}

/** 3. Sincronización de aristas con el grafo */
export async function reportActionToNeo4j(idUsuario: string, idProducto: number, relacion: 'VIO' | 'COMPRO') {
  try {
    await fetch(`${API_URL}/neo4j/accion-usuario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_usuario: idUsuario,
        id_producto: idProducto,
        relacion: relacion
      }),
    });
  } catch (error) {
    console.error("Error al reportar arista a Neo4j:", error);
  }
}