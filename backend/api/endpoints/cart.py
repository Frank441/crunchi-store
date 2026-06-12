from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import sys
import os

# Agregamos el root del backend al path para poder importar db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
try:
    from db.redis.redis_test import ControladorRedisMarketplace
except ImportError:
    # Fallback si no lo encuentra o si corre en otra ubicación
    pass

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

# Instanciamos el controlador global
try:
    redis_controller = ControladorRedisMarketplace()
except Exception as e:
    redis_controller = None

class CartItem(BaseModel):
    productId: str
    quantity: int = 1

@router.get("/{user_id}")
def get_cart(user_id: str) -> Dict[str, Any]:
    if not redis_controller:
         raise HTTPException(status_code=500, detail="No se pudo conectar a Redis.")
    try:
        carrito = redis_controller.client.hgetall(f"cart:{user_id}")
        # Convertimos las cantidades que vienen como string a entero
        items = [{"productId": k, "quantity": int(v)} for k, v in carrito.items()]
        return {"userId": user_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/add")
def add_to_cart(user_id: str, item: CartItem) -> Dict[str, Any]:
    if not redis_controller:
         raise HTTPException(status_code=500, detail="No se pudo conectar a Redis.")
    try:
        redis_controller.agregar_al_carrito(user_id, item.productId, item.quantity)
        # Devolvemos el carrito actualizado
        carrito = redis_controller.client.hgetall(f"cart:{user_id}")
        items = [{"productId": k, "quantity": int(v)} for k, v in carrito.items()]
        return {"userId": user_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
