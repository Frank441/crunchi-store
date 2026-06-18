"""
Seed de Cassandra para Crunchi Store.
350 registros en eventos_por_usuario, 550 en eventos_por_producto.

docker run --name crunchi-cassandra -p 9042:9042 -d cassandra:latest
python -m api.seed_cassandra

"""

import os
import random
import sys
from datetime import datetime
import secrets

from cassandra.cluster import Cluster
from cassandra.util import uuid_from_time
from dotenv import load_dotenv
from faker import Faker

from api.seed_50 import PRODUCTOS

load_dotenv()

fake = Faker("es_AR")

CASSANDRA_NODES = os.getenv("CASSANDRA_NODES", "127.0.0.1").split(",")
CASSANDRA_KEYSPACE = "anime_marketplace"

TOTAL_USUARIOS = 30

EVENTOS = [
    "HOME_PAGE_VISIT",
    "SEARCH",
    "VIEW_PRODUCT",
    "ADD_TO_CART",
    "REMOVE_FROM_CART",
    "CHECKOUT_START",
    "PURCHASE_COMPLETE",
    "LEAVE_REVIEW",
    "ADD_TO_WISHLIST",
]
PESOS = [0.10, 0.15, 0.35, 0.15, 0.05, 0.10, 0.05, 0.02, 0.03]

EVENTOS_PRODUCTO = [e for e in EVENTOS if e not in ["HOME_PAGE_VISIT", "SEARCH"]]


def conectar() -> tuple:
    print(f"[cassandra seed] Conectando a {CASSANDRA_NODES}...")
    cluster = Cluster(CASSANDRA_NODES)
    session = cluster.connect()
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
    """)
    session.set_keyspace(CASSANDRA_KEYSPACE)
    return session, cluster


def recrear_tablas(session) -> None:
    print("[cassandra seed] Recreando tablas...")
    session.execute("DROP TABLE IF EXISTS eventos_por_usuario;")
    session.execute("DROP TABLE IF EXISTS eventos_por_producto;")

    session.execute("""
        CREATE TABLE eventos_por_usuario (
            id_usuario  text,
            fecha_hora  timestamp,
            id_evento   timeuuid,
            evento      text,
            id_producto int,
            PRIMARY KEY (id_usuario, id_evento)
        ) WITH CLUSTERING ORDER BY (id_evento DESC);
    """)

    session.execute("""
        CREATE TABLE eventos_por_producto (
            id_producto int,
            evento      text,
            id_evento   timeuuid,
            fecha_hora  timestamp,
            id_usuario  text,
            PRIMARY KEY ((id_producto, evento), id_evento)
        ) WITH CLUSTERING ORDER BY (id_evento DESC);
    """)
    print("[cassandra seed] Tablas recreadas.")


def seed() -> None:
    session, cluster = conectar()

    try:
        recrear_tablas(session)

        ids_productos = list(range(1, len(PRODUCTOS) + 1))
        ids_usuarios = [secrets.token_hex(12) for _ in range(TOTAL_USUARIOS)]

        stmt_usuario = session.prepare("""
            INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, id_evento, evento, id_producto)
            VALUES (?, ?, ?, ?, ?)
        """)
        stmt_producto = session.prepare("""
            INSERT INTO eventos_por_producto (id_producto, evento, id_evento, fecha_hora, id_usuario)
            VALUES (?, ?, ?, ?, ?)
        """)

        # ── Tabla 1: eventos_por_usuario — 350 registros ──
        print("[cassandra seed] Insertando 350 registros en eventos_por_usuario...")
        for _ in range(350):
            id_usuario  = random.choice(ids_usuarios)
            evento      = random.choices(EVENTOS, weights=PESOS, k=1)[0]
            id_producto = random.choice(ids_productos)
            fecha_hora  = fake.date_time_between(start_date="-30d", end_date="now")
            id_evento   = uuid_from_time(fecha_hora)
            session.execute(stmt_usuario, (id_usuario, fecha_hora, id_evento, evento, id_producto))

        # ── Tabla 2: eventos_por_producto — 550 registros ──
        print("[cassandra seed] Insertando 550 registros en eventos_por_producto...")
        for _ in range(550):
            id_producto = random.choice(ids_productos)
            evento      = random.choice(EVENTOS_PRODUCTO)
            id_usuario  = random.choice(ids_usuarios)
            fecha_hora  = fake.date_time_between(start_date="-30d", end_date="now")
            id_evento   = uuid_from_time(fecha_hora)
            session.execute(stmt_producto, (id_producto, evento, id_evento, fecha_hora, id_usuario))

        print("=" * 55)
        print(f" [ÉXITO] Seed de Cassandra completado.")
        print(f" Usuarios simulados : {TOTAL_USUARIOS} (IDs 1–{TOTAL_USUARIOS})")
        print(f" Productos reales   : {len(ids_productos)} (IDs 1–{len(ids_productos)})")
        print(f" eventos_por_usuario  : 350 registros")
        print(f" eventos_por_producto : 550 registros")
        print("=" * 55)

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise
    finally:
        cluster.shutdown()


if __name__ == "__main__":
    seed()