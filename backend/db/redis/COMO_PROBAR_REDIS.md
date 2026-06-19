# Cómo probar Redis con la consola (redis-cli)

Guía rápida para inspeccionar lo que la app guarda en Redis (carrito, favoritos,
trending y sesiones).

> **Importante:** Redis corre dentro de un contenedor de Docker llamado
> `crunchi-redis`. Por eso **todos** los comandos empiezan con
> `docker exec ... crunchi-redis redis-cli`. Eso es solo "meterse" en el contenedor
> para hablarle a Redis.

---

## ¿Dónde tipeo esto?

En una terminal de **PowerShell** (la de Windows), parada en cualquier carpeta.
No hace falta estar en la del proyecto.

Hay **dos formas** de usar redis-cli. Elegí una.

---

## Forma A — Un comando por vez (la más simple)

Copiás y pegás la línea **completa** y apretás Enter. El prefijo
`docker exec crunchi-redis redis-cli` va **siempre**, y al final ponés el comando
de Redis que quieras.

```
docker exec crunchi-redis redis-cli  DBSIZE
```
```
docker exec crunchi-redis redis-cli  HGETALL cart:6a34a6e3e02f9e890661dee7
```

Estructura de cada línea:

```
docker exec crunchi-redis redis-cli   <COMANDO DE REDIS>
└──────── esto es fijo, va siempre ────┘   └─ esto cambia ─┘
```

---

## Forma B — Entrar a la consola y quedarse adentro

Si vas a tirar varios comandos seguidos, entrá **una vez**:

```
docker exec -it crunchi-redis redis-cli
```

Vas a ver que el cursor cambia a algo así:

```
127.0.0.1:6379>
```

Eso significa que ya estás **adentro**. Ahora escribís **solo el comando de Redis**
(sin el `docker exec...` adelante):

```
127.0.0.1:6379> DBSIZE
127.0.0.1:6379> HGETALL cart:6a34a6e3e02f9e890661dee7
127.0.0.1:6379> SMEMBERS wishlist:6a34a6e3e02f9e890661dee7
```

Para **salir** escribís `exit` y Enter (o Ctrl+C).

---

## Los comandos útiles (el `<COMANDO DE REDIS>`)

> El `<uid>` es el `_id` del usuario en Mongo, ej: `6a34a6e3e02f9e890661dee7`.
> Para saber cuál es el tuyo, mirá las keys con el primer comando de abajo.

| Qué quiero ver | Comando de Redis |
|---|---|
| Cuántas keys hay en total | `DBSIZE` |
| Listar todas las keys | `KEYS *` |
| Listar solo los carritos | `KEYS cart:*` |
| Ver el tipo de una key | `TYPE cart:<uid>` |
| **Carrito** (HASH: producto → cantidad) | `HGETALL cart:<uid>` |
| **Favoritos** (SET de ids de producto) | `SMEMBERS wishlist:<uid>` |
| ¿El producto 3 está en favoritos? | `SISMEMBER wishlist:<uid> 3` |
| **Trending** (ranking de más vistos) | `ZREVRANGE trending:productos 0 -1 WITHSCORES` |
| **Sesión** de un usuario | `HGETALL session:<token>` |
| Cuánto le queda a una sesión (segundos) | `TTL session:<token>` |

### Cómo se lee el resultado

- **Carrito** `HGETALL` devuelve pares: `2`, `2`, `7`, `1` → producto **2 ×2** y producto **7 ×1**.
- **Favoritos** `SMEMBERS` devuelve los ids: `3`, `10`, `15`.
- **Trending** devuelve pares id/score: `8`, `3`, `1`, `3`... → producto **8 con 3 vistas**, producto **1 con 3 vistas**, etc. (los de más arriba son los más vistos).

---

## El truco para "verlo en vivo" (recomendado para la defensa)

Abrí una terminal y dejá corriendo:

```
docker exec -it crunchi-redis redis-cli MONITOR
```

Ahora andá al navegador (http://localhost:3000) y **agregá algo al carrito** o
**marcá un favorito**. En la terminal vas a ver aparecer al instante:

```
"HINCRBY" "cart:6a34a6e3e02f9e890661dee7" "2" "1"
"SADD" "wishlist:6a34a6e3e02f9e890661dee7" "10"
"ZINCRBY" "trending:productos" "1" "5"
```

Eso prueba que la web **realmente** usa Redis (nada hardcodeado). Cortás con Ctrl+C.

---

## Comandos peligrosos (cuidado)

```
docker exec crunchi-redis redis-cli FLUSHDB
```
**Borra TODO** lo que hay en Redis (carritos, favoritos, trending, sesiones).
Solo si querés empezar de cero.
