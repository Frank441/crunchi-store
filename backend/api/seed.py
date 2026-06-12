from api.classes import ProductoCreate
from db.mongo import mongo as mongo_db


def seed() -> None:
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

    # Reinicio limpio: vaciamos catálogo y reseteamos el contador de ids.
    mongo_db.productos.delete_many({})
    mongo_db.contadores.delete_one({"_id": "productos"})
    mongo_db.init_indexes()

    documentos = []
    for p in iniciales:
        nuevo_id = mongo_db.siguiente_id("productos")
        documentos.append({"id": nuevo_id, **p.model_dump()})

    if documentos:
        mongo_db.productos.insert_many(documentos)

    print(f"[seed] {len(documentos)} productos insertados en Mongo (db='{mongo_db.MONGO_DB}').")


if __name__ == "__main__":
    seed()
