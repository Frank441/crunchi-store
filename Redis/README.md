# Módulo Redis — Crunchi Store

Demo del módulo de **memoria RAM** (Redis) para el marketplace. Levanta el servidor con Docker, instala las dependencias de Python y ejecuta la consola interactiva (`ModuloRedis-Test.py`).

## Estructuras de datos cubiertas

| Estructura | Key pattern | Uso |
|---|---|---|
| `HASH` | `cart:u_X` | Carrito de compras (producto → cantidad) con `HINCRBY` |
| `HASH + TTL` | `session:token_X` | Sesión de usuario que expira sola (`EXPIRE`) |
| `SORTED SET` | `trending:productos` | Ranking de productos más vistos (`ZINCRBY`, `ZREVRANGE`) |
| `SET` | `wishlist:u_X` | Lista de favoritos sin duplicados (`SADD`, `SMEMBERS`, `SINTER`) |

---

## 1. Requisitos

- **Docker Desktop** (Windows/macOS) o **Docker Engine** (Linux) corriendo
- **Python 3.10+**

Verificar:

```powershell
docker --version
python --version
```

---

## 2. Levantar Redis en Docker

Corré el container:

```powershell
docker run -d --name crunchi-redis -p 6379:6379 redis:7
```

| Flag | Significado |
|---|---|
| `-d` | Modo detached (en segundo plano) |
| `--name crunchi-redis` | Nombre del container para usar después |
| `-p 6379:6379` | Mapea el puerto de Redis al host |
| `redis:7` | Imagen oficial de Redis v7 |

Verificar que responde:

```powershell
docker exec crunchi-redis redis-cli PING
# -> PONG
```

> **Si ya tenés algo en el puerto 6379**, cambialo: `-p 6380:6379` y editá `host`/`port` en el constructor de `ControladorRedisMarketplace` dentro de `ModuloRedis-Test.py`.

---

## 3. Instalar dependencias de Python

```powershell
python -m pip install redis faker
```

(Las del módulo Redis no están en `requirements.txt` del repo — ese archivo es solo para MongoDB.)

---

## 4. Ejecutar la consola interactiva

```powershell
cd "crunchi-store"
$env:PYTHONIOENCODING="utf-8"
python Redis\ModuloRedis-Test.py
```

> La línea `PYTHONIOENCODING=utf-8` evita problemas con acentos y emojis (★, ♥, 💥) en la consola de Windows.

Aparece el menú:

```
==================================================
     SISTEMA EN MEMORIA REDIS - CONTROL DE DATOS
==================================================
1. Ingesta Masiva Faker (Carritos + Sesiones + Trending + Wishlist)
2. Ver Pantalla: Panel de Sesiones Activas (TTL)
3. Simular Acción de Soporte: Revocar Sesión (DEL)
4. Simular Interacción de Compra: Añadir al Carrito
5. Ver Pantalla: Mi Carrito Abierto (HGETALL)
6. Ver Top 10 Productos Trending (ZREVRANGE)
7. Registrar Vista a Producto (ZINCRBY)
8. Ver Wishlist de Usuario (SMEMBERS)
9. Agregar Producto a Wishlist (SADD)
10. Favoritos en Común entre dos Usuarios (SINTER)
11. Salir
```

---

## 5. Recorrido sugerido para defensa

| Paso | Opción | Input | Qué se ve / valida |
|---|---|---|---|
| 1 | `1` | — | Ingesta completa. `dbsize ≈ 361` (100 carritos + 200 sesiones + 1 trending + 60 wishlists) |
| 2 | `6` | — | Top 10 trending. Los primeros tienen score alto por el peso ×3 de los "populares" |
| 3 | `7` | `p_48` | `ZINCRBY` en vivo. Repetí 5 veces y volvé a `6` → `p_48` sube en el ranking |
| 4 | `2` | — | Panel de sesiones con TTL decrementando en tiempo real |
| 5 | `3` | `token_5` | `DEL` forzado: la sesión desaparece antes de su TTL natural |
| 6 | `4` | `p_naruto_3` | `HINCRBY` agrega al carrito de `u_arquitecto` |
| 7 | `5` | — | `HGETALL` del carrito |
| 8 | `8` | `u_1` | `SMEMBERS` de la wishlist (4-6 productos) |
| 9 | `9` | `u_1`, `p_99` | `SADD` agrega favorito (idempotente) |
| 10 | `10` | `u_51`, `u_107` | `SINTER` — intersección de wishlists |
| 11 | `11` | — | Salir |

---

## 6. Verificación directa con redis-cli (opcional)

Sin pasar por Python, podés inspeccionar los datos desde el container:

```powershell
docker exec -it crunchi-redis redis-cli
```

Dentro del prompt de `redis-cli`:

```redis
DBSIZE
TYPE trending:productos
ZCARD trending:productos
ZREVRANGE trending:productos 0 9 WITHSCORES
TYPE cart:u_1
HGETALL cart:u_1
TYPE session:token_1
HGETALL session:token_1
TTL session:token_1
SMEMBERS wishlist:u_1
SINTER wishlist:u_51 wishlist:u_107
```

---

## 7. Detener / limpiar

```powershell
# Pausar el container (mantiene datos en RAM)
docker stop crunchi-redis

# Volverlo a iniciar
docker start crunchi-redis

# Eliminar definitivamente (se pierde la RAM)
docker stop crunchi-redis
docker rm crunchi-redis
```

> Redis es **in-memory**: si eliminás el container, los datos se pierden. Volvé a poblar con la opción `1` cuando lo levantes de nuevo.

---

## 8. Troubleshooting

| Error | Causa | Solución |
|---|---|---|
| `Error 10061 connecting to localhost:6379` | Redis no está corriendo | `docker start crunchi-redis` o `docker run …` |
| `port is already allocated` | Otro Redis usa el 6379 | `docker ps` para ver qué container lo tiene, o usar `-p 6380:6379` |
| `ModuleNotFoundError: No module named 'redis'` | Faltan deps de Python | `python -m pip install redis faker` |
| `UnicodeEncodeError: 'charmap' …` | Consola Windows en cp1252 | `$env:PYTHONIOENCODING="utf-8"` antes de correr |
