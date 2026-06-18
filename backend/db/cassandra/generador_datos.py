import uuid
import random
from datetime import datetime, timedelta
import secrets
from faker import Faker
from cassandra.cluster import Cluster


#Para instalar Faker: pip install faker cassandra-driver 
# o python -m pip install faker cassandra-driver



fake = Faker('es_AR') # Datos localizados para Argentina

def conectar_cassandra():
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect('anime_marketplace')
    return session, cluster

# 1. Definición de Eventos Realistas con probabilidades (pesos)
EVENTOS_POSIBLES = [
    "HOME_PAGE_VISIT",
    "SEARCH",
    "VIEW_PRODUCT",
    "ADD_TO_CART",
    "REMOVE_FROM_CART",
    "CHECKOUT_START",
    "PURCHASE_COMPLETE",
    "LEAVE_REVIEW",
    "ADD_TO_WISHLIST"
]
# Probabilidad de que ocurra cada evento (más vistas que compras)
PESOS_EVENTOS = [0.10, 0.15, 0.35, 0.15, 0.05, 0.10, 0.05, 0.02, 0.03]

def generar_datos_falsos(session):
    print("Iniciando generación de datos con Faker...")

    # Generamos 50 IDs de producto (IDs del 1 al 50)
    productos_ids = list(range(1, 51))
    
    # Generamos un pool de 30 usuarios recurrentes para que el historial tenga sentido
    usuarios_ids = [secrets.token_hex(12) for _ in range(30)]

    # ========================================================
    # POBLAR TABLA 1: eventos_por_usuario (350 registros)
    # ========================================================
    print("Insertando 350 registros en 'eventos_por_usuario'...")
    query_usuario = """
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, evento, id_producto) 
        VALUES (%s, %s, %s, %s)
    """
    for _ in range(350):
        id_user = random.choice(usuarios_ids)
        # Generar una fecha aleatoria en los últimos 30 días
        fecha = fake.date_time_between(start_date='-30d', end_date='now')
        evento = random.choices(EVENTOS_POSIBLES, weights=PESOS_EVENTOS)[0]
        id_prod = random.choice(productos_ids) if evento not in ["HOME_PAGE_VISIT", "SEARCH"] else None
        
        session.execute(query_usuario, (id_user, fecha, evento, id_prod))

    # ========================================================
    # POBLAR TABLA 2: eventos_por_producto (550 registros)
    # ========================================================
    # NOTA: Rompe la consistencia del negocio, pero cumple la consigna solicitada.
    print("Insertando 550 registros en 'eventos_por_producto'...")
    query_producto = """
        INSERT INTO eventos_por_producto (id_producto, evento, fecha_hora, id_usuario) 
        VALUES (%s, %s, %s, %s)
    """
    for _ in range(550):
        id_prod = random.choice(productos_ids)
        fecha = fake.date_time_between(start_date='-30d', end_date='now')
        # Filtramos eventos que no tienen producto asociado (ej. HOME_PAGE_VISIT)
        eventos_producto = [e for e in EVENTOS_POSIBLES if e not in ["HOME_PAGE_VISIT", "SEARCH"]]
        evento = random.choice(eventos_producto)
        id_user = random.choice(usuarios_ids)
        
        session.execute(query_producto, (id_prod, evento, fecha, id_user))

    print("¡Generación de datos finalizada!")

if __name__ == "__main__":
    session, cluster = conectar_cassandra()
    try:
        generar_datos_falsos(session)
    except Exception as e:
        print(f"Error durante la inserción: {e}")
    finally:
        cluster.shutdown()