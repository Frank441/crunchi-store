import os
from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB", "crunchi")

# MongoClient es lazy, no abre conexión hasta la primera operación,
client = MongoClient(MONGO_URI)

db: Database = client[MONGO_DB]

# Colecciones.
usuarios: Collection   = db["usuarios"]    # Login / Registro.
productos: Collection  = db["productos"]   # Catálogo.
contadores: Collection = db["contadores"]  # Autoincremento de IDs enteros.


def init_indexes() -> None:
    usuarios.create_index("email", unique=True)
    productos.create_index("id", unique=True)


def siguiente_id(nombre: str) -> int:
    doc = contadores.find_one_and_update(
        {"_id": nombre},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["seq"]
