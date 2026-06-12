"use client";

import { useEffect, useState } from "react";

interface CartItem {
  productId: string;
  quantity: number;
}

interface CartResponse {
  userId: string;
  items: CartItem[];
}

export default function CartPage() {
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const userId = "u_arquitecto"; // Usuario de prueba como en el CLI de Python

  const fetchCart = async () => {
    try {
      const res = await fetch(`http://localhost:8000/cart/${userId}`);
      if (!res.ok) throw new Error("Error fetching cart");
      const data = await res.json();
      setCart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleAddToCart = async (productId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/cart/${userId}/add`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ productId, quantity: 1 }),
      });
      if (!res.ok) throw new Error("Error al agregar al carrito");
      const data = await res.json();
      setCart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 font-sans max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Mi Carrito</h1>

      {error && <div className="bg-red-100 text-red-700 p-4 rounded mb-4">{error}</div>}

      <div className="flex gap-4 mb-8">
        <button
          onClick={() => handleAddToCart(`p_${Math.floor(Math.random() * 50) + 1}`)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
          disabled={loading}
        >
          {loading ? "Cargando..." : "Agregar Manga Random"}
        </button>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="p-4 text-gray-600 font-semibold">Producto ID</th>
              <th className="p-4 text-gray-600 font-semibold">Cantidad</th>
            </tr>
          </thead>
          <tbody>
            {cart?.items && cart.items.length > 0 ? (
              cart.items.map((item, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="p-4 text-gray-800">{item.productId}</td>
                  <td className="p-4 text-gray-800 font-medium">x{item.quantity}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={2} className="p-8 text-center text-gray-500">
                  {loading ? "Cargando carrito..." : "El carrito está vacío."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
