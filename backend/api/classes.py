from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid 

class UsuarioRegister(BaseModel):
    email: EmailStr = Field(..., examples=["ana@crunchi.store"])
    password: str   = Field(..., min_length=6, examples=["secreto123"])
    alias: str      = Field(..., min_length=1, examples=["Ana"])


class UsuarioLogin(BaseModel):
    email: EmailStr = Field(..., examples=["ana@crunchi.store"])
    password: str   = Field(..., examples=["secreto123"])


class UsuarioOut(BaseModel):
    id: str
    email: EmailStr
    alias: str
    rol: str

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
    id_producto: int
    titulo: str
    relevancia: int


class SugerenciaHome(BaseModel):
    id_producto: int
    titulo: str
    puntos_afinidad: int
    
class UsuarioNeo4jInput(BaseModel):
    id_usuario: str = Field(..., examples=["60a7c9f6d4d12c001f3e7b4a"])
    alias: str      = Field(..., examples=["Maximo"])

class ProductoNeo4jInput(BaseModel):
    id_producto: int = Field(..., examples=[1])
    titulo: str      = Field(..., examples=["Berserk Vol. 1"])
    formato: str     = Field(..., examples=["Manga"])
    genero: str      = Field(..., examples=["Seinen"])

class AccionUsuarioNeo4jInput(BaseModel):
    id_usuario: str = Field(..., examples=["60a7c9f6d4d12c001f3e7b4a"])
    id_producto: int = Field(..., examples=[1])
    relacion: str    = Field(..., examples=["COMPRO"], description="'COMPRO' o 'VIO'")

# Modelos Cassandra
class EventoPorUsuarioOut(BaseModel):
    id_usuario:  str
    fecha_hora:  datetime
    id_evento:   uuid.UUID
    evento:      str
    id_producto: int
 
 
class EventoPorProductoOut(BaseModel):
    id_producto: int
    evento:      str
    id_evento:   uuid.UUID
    fecha_hora:  datetime
    id_usuario:  str
 
 
class EventoInsertInput(BaseModel):
    id_usuario:  str             = Field(..., examples=["60a7c9f6d4d12c001f3e7b4a"])
    id_producto: int             = Field(..., examples=[3])
    evento:      str             = Field(..., examples=["VIEW_PRODUCT"])
    fecha_hora:  datetime | None = Field(None, description="Si se omite, se usa el timestamp actual.")


# Modelos Redis — Carrito (HASH cart:<id_usuario>)
class CarritoItemInput(BaseModel):
    producto_id: int = Field(..., gt=0, examples=[1])
    cantidad:    int = Field(1, examples=[1], description="Delta a sumar. Negativo resta; 0 se ignora.")


class CarritoCantidadInput(BaseModel):
    cantidad: int = Field(..., ge=0, examples=[2], description="Cantidad absoluta. 0 elimina el ítem.")


class CarritoItemOut(BaseModel):
    producto: Producto
    cantidad: int
    subtotal: float


class CarritoOut(BaseModel):
    items:          list[CarritoItemOut] = Field(default_factory=list)
    total:          float = 0.0
    cantidad_items: int   = 0  # suma de cantidades (no de líneas)


class CheckoutOut(BaseModel):
    status:         str
    total:          float
    lineas:         int
    unidades:       int
    productos_comprados: list[int]


# Modelos Redis — Favoritos / Wishlist (SET wishlist:<id_usuario>)
class WishlistOut(BaseModel):
    productos:   list[Producto] = Field(default_factory=list)
    cantidad:    int = 0


# Modelos Redis — Trending (SORTED SET trending:productos)
class TrendingItemOut(BaseModel):
    producto: Producto
    vistas:   int
