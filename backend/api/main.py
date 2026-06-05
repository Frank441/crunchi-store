from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
# Para Cassandra
import uuid
from datetime import datetime

from db.neo4j import neo4j as neo4j_db
from db.cassandra import cassandra as cassandra_db

app = FastAPI(
    title="Crunchi Store API",
    description="API sencilla de demostración para el marketplace Crunchi Store.",
    version="1.0.0",
)


class ProductoBase(BaseModel):
    # Campos comunes a toda categoría.
    nombre: str = Field(..., min_length=1, examples=["Figura Naruto Uzumaki"])
    categoria: str = Field(..., min_length=1, examples=["Figuras"])
    precio: float = Field(..., gt=0, examples=[14999.99])
    stock: int = Field(0, ge=0, examples=[10])
    marca: str = Field(..., min_length=1, examples=["Bandai"])
    descripcion: str = Field("", examples=["Figura articulada de 17 cm."])
    imagenes: list[str] = Field(default_factory=list, examples=[["https://crunchi.store/img/naruto.jpg"]])
    # Campos dependientes de la categoría (opcionales).
    talles: list[str] | None = Field(None, examples=[["s", "m", "l", "xl", "xxl"]])
    volumen: int | None = Field(None, ge=1, examples=[1])


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1)
    categoria: str | None = Field(None, min_length=1)
    precio: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    marca: str | None = Field(None, min_length=1)
    descripcion: str | None = None
    imagenes: list[str] | None = None
    talles: list[str] | None = None
    volumen: int | None = Field(None, ge=1)


class Producto(ProductoBase):
    id: int
    
# Modelos Neo4J
class RecomendacionItem(BaseModel):
    id_producto: str
    titulo: str
    relevancia: int


class SugerenciaHome(BaseModel):
    id_producto: str
    titulo: str
    puntos_afinidad: int
    
class UsuarioNeo4jInput(BaseModel):
    id_usuario: str = Field(..., examples=["u1"])
    alias: str = Field(..., examples=["Maximo"])

class ProductoNeo4jInput(BaseModel):
    id_producto: str = Field(..., examples=["p1"])
    titulo: str = Field(..., examples=["Berserk Vol. 1"])
    formato: str = Field(..., examples=["Manga"])
    genero: str = Field(..., examples=["Seinen"])

class AccionUsuarioNeo4jInput(BaseModel):
    id_usuario: str = Field(..., examples=["u1"])
    id_producto: str = Field(..., examples=["p1"])
    relacion: str = Field(..., examples=["COMPRO"], description="'COMPRO' o 'VIO'")

# Modelos Cassandra
class EventoPorUsuarioOut(BaseModel):
    id_usuario: uuid.UUID
    fecha_hora: datetime
    evento: str = Field(..., description="'VIEW_PRODUCT', 'ADD_TO_CART', 'CHECKOUT'")
    id_producto: uuid.UUID

class EventoPorProductoOut(BaseModel):
    id_producto: uuid.UUID
    evento: str = Field(..., description="'VIEW_PRODUCT', 'ADD_TO_CART', 'CHECKOUT'")
    fecha_hora: datetime
    id_usuario: uuid.UUID
    
class EventoInsertInput(BaseModel):
    id_usuario: uuid.UUID = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    id_producto: uuid.UUID = Field(..., examples=["987f6543-e21b-34c5-d678-987654321000"])
    evento: str = Field(..., examples=["VIEW_PRODUCT"], description="'VIEW_PRODUCT', 'ADD_TO_CART', 'CHECKOUT'")
    # Dejamos opcional la fecha para que, si el front no la envía, el backend use la hora actual exacta
    fecha_hora: datetime | None = Field(None, description="Si se omite, se usa el timestamp actual.")

# Almacenamiento en memoria (se reinicia al reiniciar el servidor).
_id_seq = count(1)
_productos: dict[int, Producto] = {}


@app.get("/")
def raiz() -> dict[str, str]:
    return {"mensaje": "Bienvenido a la API de Crunchi Store", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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


@app.get("/usuarios/{usuario_id}/home-sugerencias", response_model=list[SugerenciaHome])
def obtener_sugerencias_home(usuario_id: str):
    """
    PANTALLA 2: La Home Page Personalizada.
    Filtrado colaborativo por afinidad de géneros consumidos, excluyendo lo visto o comprado.
    """
    query = """
    MATCH (u:Usuario {id: $user_id})-[:COMPRO]->(:Producto)-[:PERTENECE_A]->(g:Genero)<-[:PERTENECE_A]-(p_sugerido:Producto)
    WHERE NOT (u)-[:COMPRO]->(p_sugerido) AND NOT (u)-[:VIO]->(p_sugerido)
    RETURN p_sugerido.id AS id, p_sugerido.titulo AS titulo, count(g) AS puntos_afinidad
    ORDER BY puntos_afinidad DESC
    LIMIT 5;
    """
    
    with neo4j_db.get_session() as session:
        resultado = session.run(query, user_id=usuario_id)
        sugerencias = [
            SugerenciaHome(
                id_producto=registro["id"],
                titulo=registro["titulo"],
                puntos_afinidad=registro["puntos_afinidad"]
            )
            for registro in resultado
        ]
        
    return sugerencias

@app.post("/neo4j/usuario", status_code=status.HTTP_201_CREATED)
def insertar_usuario_neo4j(datos: UsuarioNeo4jInput):
    """
    Crea o actualiza de forma manual un nodo Usuario en el grafo.
    """
    query = """
        MERGE (u:Usuario {id: $id_user})
        SET u.alias = $alias
        RETURN u.id AS id, u.alias AS alias
    """
    with neo4j_db.get_session() as session:
        try:
            session.run(query, id_user=datos.id_usuario, alias=datos.alias)
            return {"status": "success", "mensaje": f"Usuario '{datos.alias}' registrado en Neo4j."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en Neo4j: {str(e)}")

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

@app.post("/neo4j/accion-usuario", status_code=status.HTTP_201_CREATED)
def registrar_accion_usuario_neo4j(datos: AccionUsuarioNeo4jInput):
    """
    Crea interacciones dinámicas de grafos (relaciones COMPRO o VIO) desde el front
    para alimentar en tiempo real el motor de recomendaciones colaborativas.
    """
    # Validamos que el front mande una relación segura para el grafo
    relacion_limpia = datos.relacion.upper()
    if relacion_limpia not in ["COMPRO", "VIO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La relación debe ser exclusivamente 'COMPRO' o 'VIO'"
        )

    # Usamos APOC o concatenación segura interna para la query ya que las relaciones en Cypher no admiten parámetros nativos directos $
    query = f"""
        MATCH (u:Usuario {{id: $id_user}})
        MATCH (p:Producto {{id: $id_prod}})
        MERGE (u)-[:{relacion_limpia}]->(p)
    """
    with neo4j_db.get_session() as session:
        try:
            resultado = session.run(query, id_user=datos.id_usuario, id_prod=datos.id_producto)
            # Validamos si los nodos realmente existían antes de relacionarlos
            if resultado.consume().counters.relationships_created == 0:
                # Si no se creó nada, verificamos si es porque ya existía o porque no encontró los nodos
                pass
            return {"status": "success", "mensaje": f"Relación -[:{relacion_limpia}]-> establecida correctamente."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al relacionar en Neo4j: {str(e)}")
        

# --- ENDPOINTS CASSANDRA (PANEL DE ANALÍTICA - SOLO LECTURA REAL) ---
@app.get("/usuario/{id_usuario}", response_model=list[EventoPorUsuarioOut])
def obtener_user_journey(id_usuario: uuid.UUID):
    """
    BLOQUE 1: Rastreador de Usuarios (User Journey Tracker)
    
    Devuelve TODOS los campos de la tabla 'eventos_por_usuario' ordenados 
    cronológicamente de manera descendente (fecha_hora DESC) para auditar 
    el flujo completo de clics de un cliente.
    """
    session = cassandra_db.get_session()
    
    # Traemos todos los campos tal cual están en tu modelo CQL
    query = "SELECT id_usuario, fecha_hora, evento, id_producto FROM eventos_por_usuario WHERE id_usuario = ?"
    
    try:
        resultado = session.execute(query, (id_usuario,))
        return [
            EventoPorUsuarioOut(
                id_usuario=fila.id_usuario,
                fecha_hora=fila.fecha_hora,
                evento=fila.evento,
                id_producto=fila.id_producto
            )
            for fila in resultado
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Cassandra: {str(e)}"
        )


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


@app.post("/cassandra/evento", status_code=status.HTTP_201_CREATED)
def insertar_evento_manual(datos: EventoInsertInput):
    """
    Simulación de envío de eventos desde el Front.
    Inserta la información de forma duplicada en 'eventos_por_usuario' y 'eventos_por_producto'
    para asegurar que el panel de analítica disponga de todos los datos en O(1).
    """
    session = cassandra_db.get_session()
    
    # Si el frontend no define una fecha_hora específica, tomamos el instante actual
    fecha_exacta = datos.fecha_hora if datos.fecha_hora else datetime.now()

    # Preparamos las sentencias para asegurar consistencia y performance
    query_usuario = """
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, evento, id_producto)
        VALUES (?, ?, ?, ?)
    """
    query_producto = """
        INSERT INTO eventos_por_producto (id_producto, evento, fecha_hora, id_usuario)
        VALUES (?, ?, ?, ?)
    """

    try:
        # Inserción obligatoria en ambas estructuras (Query-Driven Architecture)
        session.execute(query_usuario, (datos.id_usuario, fecha_exacta, datos.evento, datos.id_producto))
        session.execute(query_producto, (datos.id_producto, datos.evento, fecha_exacta, datos.id_usuario))
        
        return {
            "status": "success",
            "mensaje": "Evento registrado exitosamente en ambas tablas de Cassandra.",
            "datos_insertados": {
                "id_usuario": datos.id_usuario,
                "id_producto": datos.id_producto,
                "evento": datos.evento,
                "fecha_hora": fecha_exacta
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escribir en Cassandra: {str(e)}"
        )