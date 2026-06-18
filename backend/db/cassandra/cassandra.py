import os
from cassandra.cluster import Cluster
from dotenv import load_dotenv

load_dotenv()

CASSANDRA_NODES = os.getenv("CASSANDRA_NODES", "127.0.0.1").split(",")
CASSANDRA_KEYSPACE = "anime_marketplace"

_cluster = None
_session = None

def inicializar_cassandra():
    global _cluster, _session
    if _cluster is None:
        _cluster = Cluster(CASSANDRA_NODES)
        _session = _cluster.connect()

        _session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
        """)
        _session.set_keyspace(CASSANDRA_KEYSPACE)

        # --- Tabla 1: User Journey ---
        # Partition key: id_usuario (int, mismo que MongoDB)
        # Clustering key: id_evento (timeuuid) DESC — ordena cronológicamente
        # de forma única y sin colisiones, práctica recomendada en Cassandra
        _session.execute("""
            CREATE TABLE IF NOT EXISTS eventos_por_usuario (
                id_usuario  text,
                fecha_hora  timestamp,
                id_evento   timeuuid,
                evento      text,
                id_producto int,
                PRIMARY KEY (id_usuario, id_evento)
            ) WITH CLUSTERING ORDER BY (id_evento DESC);
        """)

        # --- Tabla 2: Embudo de Producto ---
        # Partition key compuesta: (id_producto, evento) para responder
        # "¿Quiénes hicieron ADD_TO_CART en el producto 3?" en O(1)
        # Clustering key: id_evento (timeuuid) DESC
        _session.execute("""
            CREATE TABLE IF NOT EXISTS eventos_por_producto (
                id_producto int,
                evento      text,
                id_evento   timeuuid,
                fecha_hora  timestamp,
                id_usuario  text,
                PRIMARY KEY ((id_producto, evento), id_evento)
            ) WITH CLUSTERING ORDER BY (id_evento DESC);
        """)

    return _session


def cerrar_cassandra():
    global _cluster, _session
    if _cluster is not None:
        _cluster.shutdown()
        _cluster = None
        _session = None


def get_session():
    if _session is None:
        raise RuntimeError("Cassandra no inicializado. Llamá a inicializar_cassandra() primero.")
    return _session