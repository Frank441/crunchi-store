import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    from db.mongo import mongo as mongo_db
    from db.cassandra.cassandra import inicializar_cassandra

    try:
        mongo_db.init_indexes()
        print("[OK] MongoDB inicializado correctamente.")
    except Exception as e:
        print(f"[WARN] No se pudieron crear los índices de Mongo: {e}")

    try:
        inicializar_cassandra()
        print("[OK] Cassandra inicializado correctamente.")
    except Exception as e:
        print(f"[WARN] No se pudo inicializar Cassandra: {e}")

    yield


app = FastAPI(
    title="Crunchi Store API",
    description="API sencilla de demostración para el marketplace Crunchi Store.",
    version="1.0.0",
    lifespan=lifespan,
)

# allow_credentials=True exige un origin explícito.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz() -> dict[str, str]:
    return {"mensaje": "Bienvenido a la API de Crunchi Store", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# --- Registro de rutas ---
from api.endpoints import auth, events, products, users

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(events.router)