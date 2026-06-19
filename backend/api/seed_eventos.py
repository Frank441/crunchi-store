import os
import random
import sys
from datetime import datetime
from bson import ObjectId

# Drivers de Base de Datos y dependencias de la App
from db.mongo import mongo as mongo_db 
from neo4j import GraphDatabase
from cassandra.cluster import Cluster
from cassandra.util import uuid_from_time
from dotenv import load_dotenv
from faker import Faker

# Traemos la lista de animes para mapear los géneros en Neo4j
from api.seed_50 import ANIMES

load_dotenv()
fake = Faker("es_AR")

# Configuración de Entornos para Neo4j y Cassandra
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
CASSANDRA_NODES = os.getenv("CASSANDRA_NODES", "127.0.0.1").split(",")

TOTAL_USUARIOS = 30
CASSANDRA_KEYSPACE = "anime_marketplace"

# Hash real de Bcrypt correspondiente al texto "123456"
PASSWORD_HASH_123456 = "$2b$12$7Q0V1W7Ym69F8O6XyR7ZbePqyE6Y9X2W6yB2v8K4G6z8Q2J3eR5S2"

# Mapeo de eventos de Cassandra hacia aristas de Neo4j para mantener consistencia
EVENTOS_MAP_NEO4J = {
    "VIEW_PRODUCT": "VIO",
    "PURCHASE_COMPLETE": "COMPRO"
}

EVENTOS = [
    "HOME_PAGE_VISIT", "SEARCH", "VIEW_PRODUCT", "ADD_TO_CART",
    "REMOVE_FROM_CART", "CHECKOUT_START", "PURCHASE_COMPLETE",
    "LEAVE_REVIEW", "ADD_TO_WISHLIST"
]
PESOS = [0.10, 0.15, 0.35, 0.15, 0.05, 0.10, 0.05, 0.02, 0.03]
EVENTOS_PRODUCTO = [e for e in EVENTOS if e not in ["HOME_PAGE_VISIT", "SEARCH"]]


def inicializar_conexiones():
    print("[seed] Conectando a los servicios de bases de datos...")
    
    # Neo4j
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Cassandra
    cluster = Cluster(CASSANDRA_NODES)
    session_cass = cluster.connect()
    session_cass.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
    """)
    session_cass.set_keyspace(CASSANDRA_KEYSPACE)
    
    return mongo_db, neo4j_driver, session_cass, cluster


def poblar_usuarios_mongo(mongo_ctx):
    print("[Mongo] Limpiando únicamente usuarios y generando nuevos...")
    mongo_ctx.usuarios.delete_many({})
    
    usuarios_insertados = []
    for _ in range(TOTAL_USUARIOS):
        user_id = str(ObjectId())
        user_doc = {
            "_id": ObjectId(user_id),
            "email": fake.unique.email(),
            "password_hash": PASSWORD_HASH_123456,  # Contraseña común "123456"
            "alias": fake.first_name(),
            "rol": "cliente",
            "created_at": datetime.utcnow()
        }
        usuarios_insertados.append(user_doc)
    
    mongo_ctx.usuarios.insert_many(usuarios_insertados)
    
    # Leemos la colección de productos existentes generados por seed_50 (sin borrarlos ni tocarlos)
    productos_existentes = list(mongo_ctx.productos.find({}, {"id": 1, "nombre": 1, "categoria": 1, "id_anime": 1}))
    
    print(f"[Mongo] Listo. {TOTAL_USUARIOS} usuarios creados. {len(productos_existentes)} productos detectados.")
    return usuarios_insertados, productos_existentes


def recrear_tablas_cassandra(session):
    print("[Cassandra] Recreando tablas de eventos...")
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


def poblar_neo4j_estatico(neo4j_driver, lista_usuarios, lista_productos):
    print("[Neo4j] Sincronizando nodos estáticos (Usuarios, Productos y relaciones de Género)...")
    anime_generos_map = {a["id_anime"]: a for a in ANIMES}
    
    with neo4j_driver.session() as session:
        # Limpieza completa del grafo antes de reconstruir la foto actual
        session.run("MATCH (n) DETACH DELETE n")
        
        # 1. Crear Nodos de Usuarios usando el ID hexadecimal string de Mongo
        for u in lista_usuarios:
            session.run("""
                MERGE (u:Usuario {id: $id})
                ON CREATE SET u.alias = $alias, u.email = $email
            """, id=str(u["_id"]), alias=u["alias"], email=u["email"])
            
        # 2. Crear Nodos de Productos y sus relaciones hacia sus Géneros
        for p in lista_productos:
            session.run("""
                MERGE (p:Producto {id: $id})
                ON CREATE SET p.titulo = $titulo, p.formato = $formato
            """, id=p["id"], titulo=p["nombre"], formato=p["categoria"])
            
            info_anime = anime_generos_map.get(p.get("id_anime"))
            if info_anime:
                for gen_nombre in info_anime["generos"]:
                    session.run("""
                        MERGE (g:Genero {nombre: $gen_nombre})
                        WITH g
                        MATCH (p:Producto {id: $prod_id})
                        MERGE (p)-[:PERTENECE_A]->(g)
                    """, gen_nombre=gen_nombre, prod_id=p["id"])


def registrar_relacion_neo4j(neo4j_driver, id_usuario, id_producto, tipo_relacion):
    """Crea una arista dinámica de comportamiento en Neo4j."""
    with neo4j_driver.session() as session:
        query = f"""
            MATCH (u:Usuario {{id: $id_usuario}})
            MATCH (p:Producto {{id: $id_producto}})
            MERGE (u)-[:{tipo_relacion}]->(p)
        """
        session.run(query, id_usuario=id_usuario, id_producto=int(id_producto))


def main():
    db_mongo, neo4j_driver, session_cass, cluster = inicializar_conexiones()
    
    try:
        # 1. Gestionar MongoDB sin tocar productos
        usuarios, productos = poblar_usuarios_mongo(db_mongo)
        
        ids_usuarios_mongo = [str(u["_id"]) for u in usuarios]
        ids_productos_mongo = [p["id"] for p in productos]
        
        if not ids_productos_mongo:
            print("❌ Proceso abortado: No se detectaron productos en tu MongoDB.")
            print("Asegurate de haber ejecutado: python -m api.seed_50 primero.")
            return

        # 2. Sincronizar e inicializar estructuras dependientes
        recrear_tablas_cassandra(session_cass)
        poblar_neo4j_estatico(neo4j_driver, usuarios, productos)
        
        # Declaración de statements preparados en Cassandra
        stmt_usuario = session_cass.prepare("""
            INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, id_evento, evento, id_producto)
            VALUES (?, ?, ?, ?, ?)
        """)
        stmt_producto = session_cass.prepare("""
            INSERT INTO eventos_por_producto (id_producto, evento, id_evento, fecha_hora, id_usuario)
            VALUES (?, ?, ?, ?, ?)
        """)
        
        # 3. Generar Historiales en Cassandra -> Tabla 1: eventos_por_usuario (350 registros)
        print("[Cassandra -> Neo4j] Insertando 350 registros en eventos_por_usuario...")
        for _ in range(350):
            id_usuario = random.choice(ids_usuarios_mongo)
            evento = random.choices(EVENTOS, weights=PESOS, k=1)[0]
            id_producto = random.choice(ids_productos_mongo)
            fecha_hora = fake.date_time_between(start_date="-30d", end_date="now")
            id_evento = uuid_from_time(fecha_hora)
            
            session_cass.execute(stmt_usuario, (id_usuario, fecha_hora, id_evento, evento, id_producto))
            
            # Cruzar datos con Neo4j en eventos clave (VIO / COMPRO)
            if evento in EVENTOS_MAP_NEO4J:
                registrar_relacion_neo4j(neo4j_driver, id_usuario, id_producto, EVENTOS_MAP_NEO4J[evento])

        # 4. Generar Embudos en Cassandra -> Tabla 2: eventos_por_producto (550 registros)
        print("[Cassandra -> Neo4j] Insertando 550 registros en eventos_por_producto...")
        for _ in range(550):
            id_producto = random.choice(ids_productos_mongo)
            evento = random.choice(EVENTOS_PRODUCTO)
            id_usuario = random.choice(ids_usuarios_mongo)
            fecha_hora = fake.date_time_between(start_date="-30d", end_date="now")
            id_evento = uuid_from_time(fecha_hora)
            
            session_cass.execute(stmt_producto, (id_producto, evento, id_evento, fecha_hora, id_usuario))
            
            # Cruzar datos con Neo4j
            if evento in EVENTOS_MAP_NEO4J:
                registrar_relacion_neo4j(neo4j_driver, id_usuario, id_producto, EVENTOS_MAP_NEO4J[evento])

        print("\n" + "="*60)
        print(" 🎉 [ÉXITO] Seed unificado completado con integridad total.")
        print(f" -> MongoDB   : {TOTAL_USUARIOS} usuarios nuevos con contraseña '123456'.")
        print(f" -> Neo4j     : Estructura mapeada a los productos reales de Mongo.")
        print(f" -> Cassandra : 900 eventos cruzados de forma consistente.")
        print("="*60)

    except Exception as e:
        print(f"\n❌ [ERROR] Falló la carga del seed: {e}", file=sys.stderr)
        raise
    finally:
        cluster.shutdown()
        neo4j_driver.close()


if __name__ == "__main__":
    main()