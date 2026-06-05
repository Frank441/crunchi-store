from fastapi import HTTPException, status
from itertools import count
import uuid
from db.neo4j import neo4j as neo4j_db
from db.cassandra import cassandra as cassandra_db
from api.classes import Producto, ProductoCreate, ProductoUpdate, ProductoNeo4jInput, RecomendacionItem, EventoPorProductoOut
from api.main import app


# Almacenamiento en memoria (se reinicia al reiniciar el servidor).
_id_seq = count(1)
_productos: dict[int, Producto] = {}



@app.get("/productos", response_model=list[Producto])
def listar_productos(categoria: str | None = None) -> list[Producto]:
    productos = list(_productos.values())

    if categoria is not None:
        productos = [p for p in productos if p.categoria.lower() == categoria.lower()]

    return productos


@app.get("/productos/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int) -> Producto:
    producto = _productos.get(producto_id)

    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    return producto


@app.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> Producto:
    nuevo_id = next(_id_seq)
    producto = Producto(id=nuevo_id, **datos.model_dump())
    _productos[nuevo_id] = producto

    return producto


@app.put("/productos/{producto_id}", response_model=Producto)
def actualizar_producto(producto_id: int, datos: ProductoUpdate) -> Producto:
    producto = _productos.get(producto_id)

    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    actualizado = producto.model_copy(update=cambios)
    _productos[producto_id] = actualizado

    return actualizado


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int) -> None:
    if producto_id not in _productos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    del _productos[producto_id]
    

# --- ENDPOINTS EXCLUSIVOS NEO4J (SISTEMA DE RECOMENDACIONES) ---
@app.get("/productos/{producto_id}/recomendados", response_model=list[RecomendacionItem])
def obtener_recomendados_item_based(producto_id: int):
    """
    PANTALLA 1: Detalle del Producto.
    Filtrado colaborativo Item-Based: "Los usuarios que compraron esto también compraron..."
    """
    neo4j_id = f"p{producto_id}"
    
    query = """
    MATCH (p_actual:Producto {id: $prod_id})<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(p_recomendado:Producto) 
    WHERE p_actual <> p_recomendado 
    RETURN p_recomendado.id AS id, p_recomendado.titulo AS titulo, count(u) AS relevancia 
    ORDER BY relevancia DESC 
    LIMIT 5; 
    """
    
    with neo4j_db.get_session() as session:
        resultado = session.run(query, prod_id=neo4j_id)
        recomendaciones = [
            RecomendacionItem(
                id_producto=registro["id"],
                titulo=registro["titulo"],
                relevancia=registro["relevancia"]
            )
            for registro in resultado
        ]
        
    return recomendaciones


@app.get("/producto/{id_producto}/embudo", response_model=list[EventoPorProductoOut])
def obtener_embudo_producto(id_producto: uuid.UUID, evento: str):
    """
    BLOQUE 2: Embudo por Producto (Product Conversion Funnel)
    
    Devuelve TODOS los campos de la tabla 'eventos_por_producto' filtrando por 
    la clave compuesta ((id_producto, evento)) y ordenado por tiempo (fecha_hora DESC).
    Ideal para marketing y KPIs de comportamiento caliente de compra.
    """
    session = cassandra_db.get_session()
    
    # Traemos todos los campos tal cual están en tu modelo CQL
    query = """
        SELECT id_producto, evento, fecha_hora, id_usuario 
        FROM eventos_por_producto 
        WHERE id_producto = ? AND evento = ?
    """
    
    try:
        resultado = session.execute(query, (id_producto, evento))
        return [
            EventoPorProductoOut(
                id_producto=fila.id_producto,
                evento=fila.evento,
                fecha_hora=fila.fecha_hora,
                id_usuario=fila.id_usuario
            )
            for fila in resultado
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Cassandra: {str(e)}"
        )


@app.post("/neo4j/producto", status_code=status.HTTP_201_CREATED)
def insertar_producto_completo_neo4j(datos: ProductoNeo4jInput):
    """
    Crea un nodo Producto, un nodo Genero si no existe, y establece la relación
    [:PERTENECE_A] de forma automática siguiendo el esquema del modelo.
    """
    query = """
        MERGE (p:Producto {id: $id_prod})
        SET p.titulo = $titulo, p.formato = $formato
        MERGE (g:Genero {nombre: $genero})
        MERGE (p)-[:PERTENECE_A]->(g)
    """
    with neo4j_db.get_session() as session:
        try:
            session.run(
                query, 
                id_prod=datos.id_producto, 
                titulo=datos.titulo, 
                formato=datos.formato, 
                genero=datos.genero
            )
            return {"status": "success", "mensaje": f"Producto '{datos.titulo}' enlazado a género '{datos.genero}' exitosamente."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en Neo4j: {str(e)}")
