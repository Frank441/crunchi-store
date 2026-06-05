from fastapi import FastAPI

app = FastAPI(
    title="Crunchi Store API",
    description="API sencilla de demostración para el marketplace Crunchi Store.",
    version="1.0.0",
)

@app.get("/")
def raiz() -> dict[str, str]:
    return {"mensaje": "Bienvenido a la API de Crunchi Store", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}