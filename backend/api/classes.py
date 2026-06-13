from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

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
    id_usuario:  int
    fecha_hora:  datetime
    evento:      str = Field(..., description="VIEW_PRODUCT | ADD_TO_CART | PURCHASE_COMPLETE | ...")
    id_producto: int
 
class EventoPorProductoOut(BaseModel):
    id_producto: int
    evento:      str = Field(..., description="VIEW_PRODUCT | ADD_TO_CART | PURCHASE_COMPLETE | ...")
    fecha_hora:  datetime
    id_usuario:  int
 
class EventoInsertInput(BaseModel):
    id_usuario:  int            = Field(..., examples=[1])
    id_producto: int            = Field(..., examples=[3])
    evento:      str            = Field(..., examples=["VIEW_PRODUCT"],
                                        description="VIEW_PRODUCT | ADD_TO_CART | REMOVE_FROM_CART | "
                                                    "CHECKOUT_START | PURCHASE_COMPLETE | ADD_TO_WISHLIST | LEAVE_REVIEW")
    # Si el front no lo manda, el backend usa datetime.now()
    fecha_hora:  datetime | None = Field(None, description="Si se omite, se usa el timestamp actual.")