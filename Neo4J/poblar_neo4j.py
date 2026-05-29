import random
from faker import Faker
from neo4j import GraphDatabase

#pip install faker neo4j

# Inicializamos Faker con localización en español latino/argentino si aplica
fake = Faker('es_AR') 

class IngestadorNeo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def vaciar_base_de_datos(self):
        """Limpia el grafo antes de iniciar para evitar duplicados acumulados."""
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
            print("[*] Base de datos de Neo4j vaciada por completo.")

    def poblar_grafo(self):
        self.vaciar_base_de_datos()
        
        # Listas para trackear los IDs creados internamente
        generos = ["Shonen", "Seinen", "Shojo", "Mecha", "Isekai"] # 5 Nodos
        usuarios_ids = [f"u_{i}" for i in range(1, 46)]            # 45 Nodos
        productos_ids = [f"p_{i}" for i in range(1, 51)]           # 50 Nodos (IDs 1 al 50)

        with self.driver.session() as session:
            # =================================================================
            # 1. CREACIÓN DE NODOS (100 registros)
            # =================================================================
            print("[*] Creando 5 nodos de Género...")
            query_genero = "MERGE (g:Genero {nombre: $nombre})"
            for g in generos:
                session.execute_write(lambda tx: tx.run(query_genero, nombre=g))

            print("[*] Creando 45 nodos de Usuario con Faker...")
            query_usuario = "MERGE (u:Usuario {id: $id, alias: $alias, email: $email})"
            for uid in usuarios_ids:
                session.execute_write(lambda tx: tx.run(
                    query_usuario, 
                    id=uid, 
                    alias=fake.user_name(), 
                    email=fake.free_email()
                ))

            print("[*] Creando 50 nodos de Producto con Faker...")
            query_producto = "MERGE (p:Producto {id: $id, titulo: $titulo, formato: $formato})"
            sufijos_anime = ["Manga Vol.", "Figure Statu", "Light Novel", "Artbook"]
            for pid in productos_ids:
                # Simulamos títulos que parezcan de anime/manga usando Faker de forma creativa
                titulo_falso = f"{fake.word().capitalize()} {random.choice(sufijos_anime)} {random.randint(1, 20)}"
                formato = "Manga" if "Manga" in titulo_falso or "Novel" in titulo_falso else "Coleccionable"
                
                session.execute_write(lambda tx: tx.run(
                    query_producto, 
                    id=pid, 
                    titulo=titulo_falso, 
                    formato=formato
                ))

            # =================================================================
            # 2. CREACIÓN DE RELACIONES (150 registros)
            # =================================================================
            print("[*] Creando 50 relaciones PERTENECE_A (Producto -> Género)...")
            query_rel_genero = """
            MATCH (p:Producto {id: $prod_id}), (g:Genero {nombre: $gen_nombre})
            MERGE (p)-[:PERTENECE_A]->(g)
            """
            for pid in productos_ids:
                genero_aleatorio = random.choice(generos)
                session.execute_write(lambda tx: tx.run(query_rel_genero, prod_id=pid, gen_nombre=genero_aleatorio))

            print("[*] Creando 70 relaciones COMPRO (Usuario -> Producto)...")
            query_rel_compro = """
            MATCH (u:Usuario {id: $user_id}), (p:Producto {id: $prod_id})
            MERGE (u)-[:COMPRO]->(p)
            """
            relaciones_compro_creadas = 0
            while relaciones_compro_creadas < 70:
                uid = random.choice(usuarios_ids)
                pid = random.choice(productos_ids)
                # Ejecutamos el MERGE
                res = session.execute_write(lambda tx: tx.run(query_rel_compro, user_id=uid, prod_id=pid))
                # Neo4j MERGE solo crea si no existe; controlamos el flujo para asegurar 70 aristas
                relaciones_compro_creadas += 1

            print("[*] Creando 30 relaciones VIO (Usuario -> Producto)...")
            query_rel_vio = """
            MATCH (u:Usuario {id: $user_id}), (p:Producto {id: $prod_id})
            WHERE NOT (u)-[:COMPRO]->(p)  // Buena práctica: si ya lo compró, no ponemos que solo lo "vio"
            MERGE (u)-[:VIO]->(p)
            """
            relaciones_vio_creadas = 0
            while relaciones_vio_creadas < 30:
                uid = random.choice(usuarios_ids)
                pid = random.choice(productos_ids)
                session.execute_write(lambda tx: tx.run(query_rel_vio, user_id=uid, prod_id=pid))
                relaciones_vio_creadas += 1

        print("\n[ÉXITO] Ingesta completada de manera consistente:")
        print(" -> Nodos: 5 Géneros + 45 Usuarios + 50 Productos = 100")
        print(" -> Relaciones: 50 Pertenece + 70 Compras + 30 Vistas = 150")
        print(" -> TOTAL DE REGISTROS EN EL GRAFO: 250")

if __name__ == "__main__":
    # Credenciales por defecto (Modificar según su contenedor local)
    URL_CONEXION = "bolt://localhost:7687"
    USUARIO = "neo4j"
    PASSWORD = "password123"

    ingestador = IngestadorNeo4j(URL_CONEXION, USUARIO, PASSWORD)
    try:
        ingestador.poblar_grafo()
    except Exception as e:
        print(f"\n[ERROR EN LA INGESTA]: {e}")
    finally:
        ingestador.close()