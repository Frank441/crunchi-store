from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
# Para Cassandra
import uuid
from datetime import datetime

from backend.db.neo4j import neo4j as neo4j_db
from backend.db.cassandra import cassandra as cassandra_db

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

# Almacenamiento en memoria (se reinicia al reiniciar el servidor).
_id_seq = count(1)
_productos: dict[int, Producto] = {}


def _seed() -> None:
    iniciales = [
        ProductoCreate(
            nombre="Figura Naruto Uzumaki",
            categoria="Figuras",
            precio=14999.99,
            stock=10,
            marca="Bandai",
            descripcion="Figura articulada de 17 cm de Naruto en modo Sabio.",
            imagenes=["https://crunchi.store/img/naruto.jpg"],
        ),
        ProductoCreate(
            nombre="Manga One Piece Vol. 1",
            categoria="Mangas",
            precio=8999.50,
            stock=25,
            marca="Ivrea",
            descripcion="Primer tomo de la saga de One Piece.",
            imagenes=["https://crunchi.store/img/onepiece-1.jpg"],
            volumen=1,
        ),
        ProductoCreate(
            nombre="Remera Attack on Titan",
            categoria="Indumentaria",
            precio=12500.00,
            stock=15,
            marca="Crunchi Wear",
            descripcion="Remera de algodón con estampa del Cuerpo de Exploración.",
            imagenes=["https://crunchi.store/img/aot-remera.jpg"],
            talles=["s", "m", "l", "xl", "xxl"],
        ),
    ]
    for p in iniciales:
        nuevo_id = next(_id_seq)
        _productos[nuevo_id] = Producto(id=nuevo_id, **p.model_dump())


_seed()


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
