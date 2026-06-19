"""Carrito de compras en Redis (HASH `cart:<id_usuario>`: campo=id_producto, valor=cantidad).

El carrito vive en memoria (Redis) y se enriquece con los datos del producto
desde Mongo al momento de leerlo. El checkout descuenta stock en Mongo y registra
un evento PURCHASE_COMPLETE en Cassandra (best-effort).
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from api.classes import (
    CarritoCantidadInput,
    CarritoItemInput,
    CarritoItemOut,
    CarritoOut,
    CheckoutOut,
    Producto,
)
from api.endpoints.auth import usuario_actual
from db.mongo import mongo as mongo_db
from db.redis.redis_client import client as redis_client

router = APIRouter(prefix="/carrito", tags=["carrito"])

_SIN_OBJECTID = {"_id": 0}


def _cart_key(id_usuario: str) -> str:
    return f"cart:{id_usuario}"


def _buscar_producto(producto_id: int) -> dict | None:
    return mongo_db.productos.find_one({"id": producto_id}, _SIN_OBJECTID)


def _armar_carrito(id_usuario: str) -> CarritoOut:
    """Lee el HASH del carrito y lo enriquece con los productos de Mongo."""
    bruto = redis_client.hgetall(_cart_key(id_usuario))  # {str(id): str(cant)}
    items: list[CarritoItemOut] = []
    total = 0.0
    unidades = 0

    for pid_str, cant_str in bruto.items():
        cantidad = int(cant_str)
        doc = _buscar_producto(int(pid_str))
        if doc is None:
            # Producto borrado del catálogo: lo limpiamos del carrito.
            redis_client.hdel(_cart_key(id_usuario), pid_str)
            continue
        producto = Producto(**doc)
        subtotal = producto.precio * cantidad
        total += subtotal
        unidades += cantidad
        items.append(CarritoItemOut(producto=producto, cantidad=cantidad, subtotal=subtotal))

    items.sort(key=lambda it: it.producto.id)
    return CarritoOut(items=items, total=total, cantidad_items=unidades)


@router.get("", response_model=CarritoOut)
def ver_carrito(sesion: dict = Depends(usuario_actual)) -> CarritoOut:
    return _armar_carrito(sesion["id_usuario"])


@router.post("/items", response_model=CarritoOut, status_code=status.HTTP_201_CREATED)
def agregar_item(datos: CarritoItemInput, sesion: dict = Depends(usuario_actual)) -> CarritoOut:
    id_usuario = sesion["id_usuario"]

    producto = _buscar_producto(datos.producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if datos.cantidad == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad no puede ser 0")

    key = _cart_key(id_usuario)
    campo = str(datos.producto_id)

    # HINCRBY: suma/resta atómica sobre el campo del producto.
    nueva_cantidad = redis_client.hincrby(key, campo, datos.cantidad)

    # No permitimos cantidades negativas ni superar el stock disponible.
    if nueva_cantidad <= 0:
        redis_client.hdel(key, campo)
    elif nueva_cantidad > producto["stock"]:
        redis_client.hset(key, campo, producto["stock"])

    return _armar_carrito(id_usuario)


@router.put("/items/{producto_id}", response_model=CarritoOut)
def fijar_cantidad(
    producto_id: int,
    datos: CarritoCantidadInput,
    sesion: dict = Depends(usuario_actual),
) -> CarritoOut:
    id_usuario = sesion["id_usuario"]
    key = _cart_key(id_usuario)
    campo = str(producto_id)

    producto = _buscar_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if datos.cantidad == 0:
        redis_client.hdel(key, campo)
    else:
        cantidad = min(datos.cantidad, producto["stock"])
        redis_client.hset(key, campo, cantidad)

    return _armar_carrito(id_usuario)


@router.delete("/items/{producto_id}", response_model=CarritoOut)
def quitar_item(producto_id: int, sesion: dict = Depends(usuario_actual)) -> CarritoOut:
    id_usuario = sesion["id_usuario"]
    redis_client.hdel(_cart_key(id_usuario), str(producto_id))
    return _armar_carrito(id_usuario)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def vaciar_carrito(sesion: dict = Depends(usuario_actual)) -> None:
    redis_client.delete(_cart_key(sesion["id_usuario"]))


@router.post("/checkout", response_model=CheckoutOut)
def checkout(sesion: dict = Depends(usuario_actual)) -> CheckoutOut:
    """Confirma la compra: valida stock, lo descuenta en Mongo, registra el evento
    PURCHASE_COMPLETE en Cassandra y vacía el carrito en Redis."""
    id_usuario = sesion["id_usuario"]
    carrito = _armar_carrito(id_usuario)

    if not carrito.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

    # Validación de stock antes de tocar nada.
    sin_stock = [it.producto.nombre for it in carrito.items if it.cantidad > it.producto.stock]
    if sin_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock insuficiente para: {', '.join(sin_stock)}",
        )

    comprados: list[int] = []
    for it in carrito.items:
        mongo_db.productos.update_one({"id": it.producto.id}, {"$inc": {"stock": -it.cantidad}})
        comprados.append(it.producto.id)
        _registrar_compra_cassandra(id_usuario, it.producto.id)

    redis_client.delete(_cart_key(id_usuario))

    return CheckoutOut(
        status="success",
        total=carrito.total,
        lineas=len(carrito.items),
        unidades=carrito.cantidad_items,
        productos_comprados=comprados,
    )


def _registrar_compra_cassandra(id_usuario: str, producto_id: int) -> None:
    """Best-effort: si Cassandra no está disponible, la compra igual se concreta."""
    try:
        from cassandra.util import uuid_from_time
        from db.cassandra import cassandra as cassandra_db

        session = cassandra_db.get_session()
        ahora = datetime.now()
        id_evento = uuid_from_time(ahora)
        session.execute(
            """INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, id_evento, evento, id_producto)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_usuario, ahora, id_evento, "PURCHASE_COMPLETE", producto_id),
        )
        session.execute(
            """INSERT INTO eventos_por_producto (id_producto, evento, id_evento, fecha_hora, id_usuario)
               VALUES (%s, %s, %s, %s, %s)""",
            (producto_id, "PURCHASE_COMPLETE", id_evento, ahora, id_usuario),
        )
    except Exception as e:  # noqa: BLE001 — no queremos romper el checkout por analítica.
        print(f"[WARN] No se pudo registrar PURCHASE_COMPLETE en Cassandra: {e}")
