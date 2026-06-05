from api.index import app
from api.index import Router

router = Router.getInstance()

mongo = router.mongo


@app.get("/productos", response_model=list[Producto])
def listar_productos(categoria: str | None = None) -> list[Producto]:
    productos = list(mongo.values())

    if categoria is not None:
        productos = [p for p in productos if p.categoria.lower() == categoria.lower()]

    return productos