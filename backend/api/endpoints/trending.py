"""Productos trending en Redis (SORTED SET `trending:productos`, score = nº de vistas).

Cada visita a la ficha de un producto suma 1 al score (ZINCRBY) y el ranking
se lee con ZREVRANGE (mayor score primero).
"""
from fastapi import APIRouter, Depends

from api.classes import Producto, TrendingItemOut
from api.endpoints.auth import usuario_actual
from db.mongo import mongo as mongo_db
from db.redis.redis_client import client as redis_client

router = APIRouter(prefix="/trending", tags=["trending"])

_TRENDING_KEY = "trending:productos"
_SIN_OBJECTID = {"_id": 0}


@router.post("/vista/{producto_id}", status_code=200)
def registrar_vista(producto_id: int) -> dict:
    """ZINCRBY: suma 1 vista al producto en el ranking en tiempo real.

    Público (no requiere sesión): se llama al abrir la ficha del producto.
    """
    nuevo_score = redis_client.zincrby(_TRENDING_KEY, 1, producto_id)
    return {"producto_id": producto_id, "vistas": int(nuevo_score)}


@router.get("", response_model=list[TrendingItemOut])
def top_trending(limit: int = 10) -> list[TrendingItemOut]:
    """ZREVRANGE WITHSCORES: top N productos más vistos, enriquecidos desde Mongo."""
    ranking = redis_client.zrevrange(_TRENDING_KEY, 0, limit - 1, withscores=True)
    if not ranking:
        return []

    ids = [int(pid) for pid, _ in ranking]
    docs = {d["id"]: d for d in mongo_db.productos.find({"id": {"$in": ids}}, _SIN_OBJECTID)}

    salida: list[TrendingItemOut] = []
    for pid, score in ranking:
        doc = docs.get(int(pid))
        if doc is not None:
            salida.append(TrendingItemOut(producto=Producto(**doc), vistas=int(score)))
    return salida
