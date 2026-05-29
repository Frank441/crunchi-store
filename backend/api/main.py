from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

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
