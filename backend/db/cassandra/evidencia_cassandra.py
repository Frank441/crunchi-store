import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement


#Ejecutar en terminal:
#pip install cassandra-driver



# =====================================================================
# DATOS PREDEFINIDOS PARA LA DEMOSTRACIÓN (Evita tipear UUIDs en vivo)
# =====================================================================
USUARIOS_DEMO = {
    "1": {"nombre": "Matias_Otaku", "id": uuid.uuid4()},
    "2": {"nombre": "Lucia_Coleccionista", "id": uuid.uuid4()}
}

PRODUCTOS_DEMO = {
    "1": {"nombre": "Tomo 1 - Berserk (Manga)", "id": uuid.uuid4()},
    "2": {"nombre": "Figura Makima 1/4 (Escala)", "id": uuid.uuid4()}
}

EVENTOS_PERMITIDOS = ["VIEW_PRODUCT", "ADD_TO_CART", "CHECKOUT", "LEAVE_REVIEW"]

# =====================================================================
# CONEXIÓN Y LÓGICA DE NEGOCIO (BBDD)
# =====================================================================
def conectar_cassandra():
    print("[*] Conectando al clúster de Cassandra...")
    cluster = Cluster(['127.0.0.1'], port=9042)
    session = cluster.connect()
    session.set_keyspace('anime_marketplace')
    return session, cluster

def registrar_evento_marketplace(session, id_usuario, id_producto, tipo_evento):
    fecha_actual = datetime.now()
    batch = BatchStatement()

    # 1. Inserción para la vista del Usuario
    query_usuario = SimpleStatement("""
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, evento, id_producto) 
        VALUES (%s, %s, %s, %s)
    """)
    batch.add(query_usuario, (id_usuario, fecha_actual, tipo_evento, id_producto))

    # 2. Inserción para la vista del Producto
    query_producto = SimpleStatement("""
        INSERT INTO eventos_por_producto (id_producto, evento, fecha_hora, id_usuario) 
        VALUES (%s, %s, %s, %s)
    """)
    batch.add(query_producto, (id_producto, tipo_evento, fecha_actual, id_usuario))

    session.execute(batch)
    print(f"\n[ÉXITO] Evento '{tipo_evento}' guardado en ambas tablas (BATCH).")

def mostrar_historial_usuario(session, id_usuario, nombre_usuario):
    print(f"\n--- HISTORIAL DE NAVEGACIÓN: {nombre_usuario} ---")
    query = "SELECT fecha_hora, evento, id_producto FROM eventos_por_usuario WHERE id_usuario = %s LIMIT 10"
    rows = session.execute(query, (id_usuario,))
    
    contador = 0
    for row in rows:
        contador += 1
        print(f"  -> [{row.fecha_hora}] | Acción: {row.evento} | Prod_ID: {row.id_producto}")
    
    if contador == 0:
        print("  (No hay eventos registrados para este usuario)")

def mostrar_embudo_producto(session, id_producto, nombre_producto, tipo_evento):
    print(f"\n--- EMBUDO: Usuarios que hicieron '{tipo_evento}' en '{nombre_producto}' ---")
    query = "SELECT fecha_hora, id_usuario FROM eventos_por_producto WHERE id_producto = %s AND evento = %s LIMIT 10"
    rows = session.execute(query, (id_producto, tipo_evento))
    
    contador = 0
    for row in rows:
        contador += 1
        print(f"  -> [{row.fecha_hora}] | Usuario_ID: {row.id_usuario}")
        
    if contador == 0:
        print(f"  (No hay eventos de tipo {tipo_evento} para este producto)")

# =====================================================================
# INTERFAZ DE TERMINAL (CLI)
# =====================================================================
def menu_interactivo(session):
    while True:
        print("\n" + "="*50)
        print("  MARKETPLACE ANIME - PANEL DE CONTROL CASSANDRA  ")
        print("="*50)
        print("1. Simular recorrido completo (View -> Cart -> Checkout)")
        print("2. Registrar evento individual manual")
        print("3. Consultar Historial de un Usuario (Modelo 1)")
        print("4. Consultar Embudo de un Producto (Modelo 2)")
        print("5. Salir")
        
        opcion = input("\nSeleccioná una opción (1-5): ")

        if opcion == "1":
            print("\nSimulando que 'Matias_Otaku' compra el 'Tomo 1 - Berserk'...")
            user_id = USUARIOS_DEMO["1"]["id"]
            prod_id = PRODUCTOS_DEMO["1"]["id"]
            
            registrar_evento_marketplace(session, user_id, prod_id, 'VIEW_PRODUCT')
            registrar_evento_marketplace(session, user_id, prod_id, 'ADD_TO_CART')
            registrar_evento_marketplace(session, user_id, prod_id, 'CHECKOUT')

        elif opcion == "2":
            print("\nUsuarios disponibles: 1) Matias_Otaku  2) Lucia_Coleccionista")
            opt_u = input("Elegí usuario (1/2): ")
            print("Productos disponibles: 1) Tomo Berserk  2) Figura Makima")
            opt_p = input("Elegí producto (1/2): ")
            print("Eventos: VIEW_PRODUCT, ADD_TO_CART, CHECKOUT, LEAVE_REVIEW")
            evento = input("Escribí el evento: ").upper()
            
            if opt_u in USUARIOS_DEMO and opt_p in PRODUCTOS_DEMO and evento in EVENTOS_PERMITIDOS:
                registrar_evento_marketplace(
                    session, 
                    USUARIOS_DEMO[opt_u]["id"], 
                    PRODUCTOS_DEMO[opt_p]["id"], 
                    evento
                )
            else:
                print("\n[ERROR] Opciones inválidas o evento mal escrito.")

        elif opcion == "3":
            print("\nUsuarios: 1) Matias_Otaku  2) Lucia_Coleccionista")
            opt_u = input("De qué usuario querés ver el historial? (1/2): ")
            if opt_u in USUARIOS_DEMO:
                mostrar_historial_usuario(session, USUARIOS_DEMO[opt_u]["id"], USUARIOS_DEMO[opt_u]["nombre"])
            else:
                print("[ERROR] Usuario inválido.")

        elif opcion == "4":
            print("\nProductos: 1) Tomo Berserk  2) Figura Makima")
            opt_p = input("De qué producto querés ver el embudo? (1/2): ")
            evento = input("Qué evento querés filtrar? (ej. ADD_TO_CART): ").upper()
            if opt_p in PRODUCTOS_DEMO and evento in EVENTOS_PERMITIDOS:
                mostrar_embudo_producto(session, PRODUCTOS_DEMO[opt_p]["id"], PRODUCTOS_DEMO[opt_p]["nombre"], evento)
            else:
                print("[ERROR] Producto o evento inválido.")

        elif opcion == "5":
            print("\nCerrando conexión. ¡Éxitos en la presentación!")
            break
        else:
            print("\n[ERROR] Opción no válida. Ingresá un número del 1 al 5.")

if __name__ == "__main__":
    try:
        session, cluster = conectar_cassandra()
        menu_interactivo(session)
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] No se pudo conectar o ejecutar: {e}")
        print("Asegurate de que el contenedor de Cassandra esté corriendo en el puerto 9042.")
    finally:
        if 'cluster' in locals():
            cluster.shutdown()