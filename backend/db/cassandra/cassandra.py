import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv

load_dotenv()

CASSANDRA_NODES = os.getenv("CASSANDRA_NODES", "127.0.0.1").split(",")
CASSANDRA_KEYSPACE = "anime_marketplace"

_cluster = None
_session = None

def inicializar_cassandra():
    global _cluster, _session
    if _cluster is None:
        # Podés agregar credenciales aquí si tu Cassandra las requiere en producción
        _cluster = Cluster(CASSANDRA_NODES)
        _session = _cluster.connect()
        
        # Creamos el Keyspace y las Tablas de manera automática (Idempotente)
        _session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
        """)
        _session.set_keyspace(CASSANDRA_KEYSPACE)
        
        # Tabla 1: User Journey
        _session.execute("""
            CREATE TABLE IF NOT EXISTS eventos_por_usuario (
                id_usuario uuid,
                fecha_hora timestamp,
                evento text,
                id_producto uuid,
                PRIMARY KEY (id_usuario, fecha_hora)
            ) WITH CLUSTERING ORDER BY (fecha_hora DESC);
        """)
        
        # Tabla 2: Embudo de Producto
        _session.execute("""
            CREATE TABLE IF NOT EXISTS eventos_por_producto (
                id_producto uuid,
                evento text,
                fecha_hora timestamp,
                id_usuario uuid,
                PRIMARY KEY ((id_producto, evento), fecha_hora)
            ) WITH CLUSTERING ORDER BY (fecha_hora DESC);
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
        raise RuntimeError("Cassandra no inicializado.")
    return _session