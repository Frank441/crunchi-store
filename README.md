<p align="center">
  <img src="https://github.com/Frank441/crunchi-store/blob/fd3920bf3cc5058843ecc82afd800f14cd1c48c4/frontend/public/crunchi_store_logo.png" alt="Crunchi Store" width="500"/>
</p>


## API (FastAPI)

### 1. Requisitos

- **Python 3.10+**

```powershell
python --version
```

### 2. Crear y activar el entorno virtual

Desde la carpeta `backend`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la activación con `... no se puede cargar porque la ejecución de scripts está deshabilitada`, habilitala solo para tu usuario:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> En macOS/Linux la activación es `source .venv/bin/activate`.

Con el venv activo, el prompt muestra el prefijo `(.venv)`.

### 3. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Levantar las bases de datos

Utilizando Docker:

```powershell
docker run -d --name crunchi-redis -p 6379:6379 redis:latest
docker run -d --name crunchi-mongo -p 27017:27017 mongo:8  
docker run -d --name crunchi-cassandra -p 9042:9042 cassandra:latest
docker run -d --name crunchi-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

Para registrar los productos base de MongoDB, utilizar desde la carpeta `backend` (con el venv activo):

```powershell
python -m api.seed_50
```

Y para los dataset de Cassandra y Neo4j + usuarios falsos en MongoDB
```powershell
python -m api.seed_eventos
```

### 5. Levantar la API

Desde la carpeta `backend` (con el venv activo):

```powershell
uvicorn api.main:app --reload
```

| Flag | Significado |
|---|---|
| `api.main:app` | Módulo `api/main.py`, objeto `app` de FastAPI |
| `--reload` | Recarga automática al editar el código (solo para desarrollo) |

La API queda disponible en `http://127.0.0.1:8000`.

### 6. Levantar el frontend
Abrir una nueva terminal

Desde la carpeta `frontend`

En desarrollo:

```powershell
npm run dev
```

En producción:
```powershell
npm build && npm start
```

### 7. Probar

- Documentación interactiva (Swagger UI): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Listado de productos: http://127.0.0.1:8000/productos
- Page de Cassandra: http://localhost:3000/analitica

### 8. Detener / salir

- Detener el servidor: `Ctrl + C`
- Salir del entorno virtual: `deactivate`
