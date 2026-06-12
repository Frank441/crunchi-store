from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import sys
import os

try:
    from db.redis.redis_client import client as redis_client
except ImportError:
    redis_client = None

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

class CartItem(BaseModel):
    productId: str
    quantity: int = 1

@router.get("/{user_id}")
def get_cart(user_id: str) -> Dict[str, Any]:
    if not redis_client:
         raise HTTPException(status_code=500, detail="No se pudo conectar a Redis.")
    try:
        carrito = redis_client.hgetall(f"cart:{user_id}")
        # Convertimos las cantidades que vienen como string a entero
        items = [{"productId": k, "quantity": int(v)} for k, v in carrito.items()]
        return {"userId": user_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/add")
def add_to_cart(user_id: str, item: CartItem) -> Dict[str, Any]:
    if not redis_client:
         raise HTTPException(status_code=500, detail="No se pudo conectar a Redis.")
    try:
        # HINCRBY muta el valor numérico del campo de forma directa y segura
        nuevo_stock = redis_client.hincrby(f"cart:{user_id}", item.productId, item.quantity)
        
        # Imprimir en consola (para ver en los logs del docker/terminal)
        print(f"[CARRITO] Agregado ID: {item.productId} | Stock en carrito: {nuevo_stock}", flush=True)
        
        # Devolvemos el carrito actualizado
        carrito = redis_client.hgetall(f"cart:{user_id}")
        items = [{"productId": k, "quantity": int(v)} for k, v in carrito.items()]
        return {"userId": user_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
