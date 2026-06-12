# crunchi-store
Repositorio de la plataforma Crunchi Store.

Este proyecto está dividido en un frontend (React/Next.js) y un backend (FastAPI), utilizando Redis como base de datos en memoria para manejar el carrito de compras.

---

## 1. Requisitos Previos

Asegúrate de tener instalado en tu sistema lo siguiente:
- **Python 3.10+**
- **Node.js** (versión 18 o superior recomendada)
- **Docker Desktop** (para levantar la base de datos Redis)

---

## 2. Base de Datos (Redis)

El backend requiere una instancia de Redis corriendo para manejar el carrito de compras.

Abre tu terminal y ejecuta el siguiente comando de Docker para levantar un contenedor de Redis:
```powershell
docker run -d --name redis -p 6379:6379 redis
```
> Esto descargará la imagen (si no la tienes) y dejará Redis corriendo en segundo plano en el puerto 6379.

---

## 3. Backend (API con FastAPI)

### Instalar dependencias y preparar el entorno

Desde la carpeta raíz del proyecto, entra a `backend` y crea un entorno virtual:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la activación con `... no se puede cargar porque la ejecución de scripts está deshabilitada`, habilítala solo para tu usuario:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> En macOS/Linux la activación es `source .venv/bin/activate`.

Con el venv activo, el prompt mostrará el prefijo `(.venv)`. Instala las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Levantar la API

Con las dependencias instaladas y el entorno virtual activado, ejecuta:

```powershell
uvicorn api.main:app --reload --port 8000
```

| Flag | Significado |
|---|---|
| `api.main:app` | Módulo `api/main.py`, objeto `app` de FastAPI |
| `--reload` | Recarga automática al editar el código (solo desarrollo) |
| `--port 8000` | Fija el puerto en 8000 para que coincida con lo que espera el frontend |

La API quedará disponible en `http://127.0.0.1:8000`.

**Endpoints útiles para probar:**
- Documentación interactiva (Swagger UI): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Para detener la API, presiona `Ctrl + C`. Para salir del entorno virtual, escribe `deactivate`.

---

## 4. Frontend (React / Next.js)

### Instalar dependencias

Abre una **nueva pestaña** en tu terminal (para no cerrar el backend), entra a la carpeta `frontend` y descarga los paquetes de Node:

```powershell
cd frontend
npm install
```

### Levantar la web

Ejecuta el servidor de desarrollo:

```powershell
npm run dev
```

La página web quedará disponible en `http://localhost:3000`. 
Puedes probar ingresando a rutas como `http://localhost:3000/cart` para ver la interacción con el backend y Redis.
