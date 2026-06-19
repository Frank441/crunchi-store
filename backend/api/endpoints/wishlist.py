"""Favoritos / Wishlist en Redis (SET `wishlist:<id_usuario>` de id_producto).

El SET garantiza que no haya favoritos duplicados (SADD es idempotente).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from api.classes import Producto, WishlistOut
from api.endpoints.auth import usuario_actual
from db.mongo import mongo as mongo_db
from db.redis.redis_client import client as redis_client

router = APIRouter(prefix="/favoritos", tags=["favoritos"])

_SIN_OBJECTID = {"_id": 0}


def _wishlist_key(id_usuario: str) -> str:
    return f"wishlist:{id_usuario}"


@router.get("", response_model=WishlistOut)
def ver_favoritos(sesion: dict = Depends(usuario_actual)) -> WishlistOut:
    """SMEMBERS + enriquecido con los productos de Mongo."""
    ids = redis_client.smembers(_wishlist_key(sesion["id_usuario"]))
    if not ids:
        return WishlistOut(productos=[], cantidad=0)

    ids_int = sorted(int(i) for i in ids)
    docs = mongo_db.productos.find({"id": {"$in": ids_int}}, _SIN_OBJECTID)
    productos = sorted((Producto(**d) for d in docs), key=lambda p: p.id)
    return WishlistOut(productos=productos, cantidad=len(productos))


@router.get("/ids", response_model=list[int])
def ver_favoritos_ids(sesion: dict = Depends(usuario_actual)) -> list[int]:
    """Solo los ids — liviano para pintar el estado de los corazones en el catálogo."""
    ids = redis_client.smembers(_wishlist_key(sesion["id_usuario"]))
    return sorted(int(i) for i in ids)


@router.post("/{producto_id}", status_code=status.HTTP_201_CREATED)
def agregar_favorito(producto_id: int, sesion: dict = Depends(usuario_actual)) -> dict:
    if mongo_db.productos.find_one({"id": producto_id}, _SIN_OBJECTID) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    agregados = redis_client.sadd(_wishlist_key(sesion["id_usuario"]), producto_id)
    return {
        "status": "success",
        "producto_id": producto_id,
        "ya_estaba": agregados == 0,
        "es_favorito": True,
    }


@router.delete("/{producto_id}", status_code=status.HTTP_200_OK)
def quitar_favorito(producto_id: int, sesion: dict = Depends(usuario_actual)) -> dict:
    redis_client.srem(_wishlist_key(sesion["id_usuario"]), producto_id)
    return {"status": "success", "producto_id": producto_id, "es_favorito": False}
