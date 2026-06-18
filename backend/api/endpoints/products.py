from fastapi import APIRouter, HTTPException, status

from api.classes import (
    EventoPorProductoOut,
    Producto,
    ProductoCreate,
    ProductoNeo4jInput,
    ProductoUpdate,
    RecomendacionItem,
)
from db.cassandra import cassandra as cassandra_db
from db.mongo import mongo as mongo_db
from db.neo4j import neo4j as neo4j_db

router = APIRouter(tags=["productos"])

_SIN_OBJECTID = {"_id": 0}


# --- MONGO ---

@router.get("/productos", response_model=list[Producto])
def listar_productos(categoria: str | None = None) -> list[Producto]:
    filtro: dict = {}
    if categoria is not None:
        filtro["categoria"] = {"$regex": f"^{categoria}$", "$options": "i"}
    documentos = mongo_db.productos.find(filtro, _SIN_OBJECTID)
    return [Producto(**doc) for doc in documentos]


@router.get("/productos/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int) -> Producto:
    doc = mongo_db.productos.find_one({"id": producto_id}, _SIN_OBJECTID)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return Producto(**doc)


@router.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> Producto:
    nuevo_id = mongo_db.siguiente_id("productos")
    documento = {"id": nuevo_id, **datos.model_dump()}
    mongo_db.productos.insert_one(documento)
    return Producto(id=nuevo_id, **datos.model_dump())


@router.put("/productos/{producto_id}", response_model=Producto)
def actualizar_producto(producto_id: int, datos: ProductoUpdate) -> Producto:
    cambios = datos.model_dump(exclude_unset=True)
    doc = mongo_db.productos.find_one_and_update(
        {"id": producto_id},
        {"$set": cambios},
        projection=_SIN_OBJECTID,
        return_document=True,
    )
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return Producto(**doc)


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int) -> None:
    resultado = mongo_db.productos.delete_one({"id": producto_id})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")


# --- NEO4J ---

@router.get("/productos/{producto_id}/recomendados", response_model=list[RecomendacionItem])
def obtener_recomendados_item_based(producto_id: int):
    query = """
    MATCH (p_actual:Producto {id: $prod_id})<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(p_recomendado:Producto)
    WHERE p_actual <> p_recomendado
    RETURN p_recomendado.id AS id, p_recomendado.titulo AS titulo, count(u) AS relevancia
    ORDER BY relevancia DESC
    LIMIT 5;
    """
    with neo4j_db.get_session() as session:
        resultado = session.run(query, prod_id=producto_id)
        return [
            RecomendacionItem(
                id_producto=registro["id"],
                titulo=registro["titulo"],
                relevancia=registro["relevancia"],
            )
            for registro in resultado
        ]


@router.post("/neo4j/producto", status_code=status.HTTP_201_CREATED)
def insertar_producto_completo_neo4j(datos: ProductoNeo4jInput):
    query = """
        MERGE (p:Producto {id: $id_prod})
        SET p.titulo = $titulo, p.formato = $formato
        MERGE (g:Genero {nombre: $genero})
        MERGE (p)-[:PERTENECE_A]->(g)
    """
    with neo4j_db.get_session() as session:
        try:
            session.run(query, id_prod=datos.id_producto, titulo=datos.titulo, formato=datos.formato, genero=datos.genero)
            return {"status": "success", "mensaje": f"Producto '{datos.titulo}' enlazado a género '{datos.genero}' exitosamente."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en Neo4j: {str(e)}")


# --- CASSANDRA ---

@router.get("/producto/{id_producto}/embudo", response_model=list[EventoPorProductoOut])
def obtener_embudo_producto(id_producto: int, evento: str, limit: int = 50):
    session = cassandra_db.get_session()
    
    # Añadimos LIMIT dinámico en la consulta CQL preparado para Cassandra
    query = session.prepare("""
        SELECT id_producto, evento, id_evento, fecha_hora, id_usuario
        FROM eventos_por_producto
        WHERE id_producto = ? AND evento = ?
        LIMIT ?
    """)
    try:
        # Pasamos el parámetro de limitación a la ejecución de la consulta
        resultado = session.execute(query, (id_producto, evento.upper(), limit))
        return [
            EventoPorProductoOut(
                id_producto=fila.id_producto,
                evento=fila.evento,
                id_evento=fila.id_evento,
                fecha_hora=fila.fecha_hora,
                id_usuario=fila.id_usuario,
            )
            for fila in resultado
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Cassandra: {str(e)}",
        )