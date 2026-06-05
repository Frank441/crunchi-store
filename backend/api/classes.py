from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class ProductoBase(BaseModel):
    # Campos comunes a toda categoría.
    nombre: str              = Field(..., min_length=1, examples=["Figura Naruto Uzumaki"])
    categoria: str           = Field(..., min_length=1, examples=["Figuras"])
    precio: float            = Field(..., gt=0, examples=[14999.99])
    stock: int               = Field(0, ge=0, examples=[10])
    marca: str               = Field(..., min_length=1, examples=["Bandai"])
    descripcion: str         = Field("", examples=["Figura articulada de 17 cm."])
    imagenes: list[str]      = Field(default_factory=list, examples=[["https://crunchi.store/img/naruto.jpg"]])
    # Campos dependientes de la categoría (opcionales).
    talles: list[str] | None = Field(None, examples=[["s", "m", "l", "xl", "xxl"]])
    volumen: int | None      = Field(None, ge=1, examples=[1])


# Operaciones

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: str | None         = Field(None, min_length=1)
    categoria: str | None      = Field(None, min_length=1)
    precio: float | None       = Field(None, gt=0)
    stock: int | None          = Field(None, ge=0)
    marca: str | None          = Field(None, min_length=1)
    descripcion: str | None    = None
    imagenes: list[str] | None = None
    talles: list[str] | None   = None
    volumen: int | None        = Field(None, ge=1)


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
    alias: str      = Field(..., examples=["Maximo"])

class ProductoNeo4jInput(BaseModel):
    id_producto: str = Field(..., examples=["p1"])
    titulo: str      = Field(..., examples=["Berserk Vol. 1"])
    formato: str     = Field(..., examples=["Manga"])
    genero: str      = Field(..., examples=["Seinen"])

class AccionUsuarioNeo4jInput(BaseModel):
    id_usuario: str  = Field(..., examples=["u1"])
    id_producto: str = Field(..., examples=["p1"])
    relacion: str    = Field(..., examples=["COMPRO"], description="'COMPRO' o 'VIO'")

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
    id_usuario: uuid.UUID       = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    id_producto: uuid.UUID      = Field(..., examples=["987f6543-e21b-34c5-d678-987654321000"])
    evento: str                 = Field(..., examples=["VIEW_PRODUCT"], description="'VIEW_PRODUCT', 'ADD_TO_CART', 'CHECKOUT'")
    # Dejamos opcional la fecha para que, si el front no la envía, el backend use la hora actual exacta
    fecha_hora: datetime | None = Field(None, description="Si se omite, se usa el timestamp actual.")
