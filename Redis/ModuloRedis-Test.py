import redis
import random
from faker import Faker

#python -m pip install redis faker

fake = Faker('es_AR')

class ControladorRedisMarketplace:
    def __init__(self, host='localhost', port=6379, db=0):
        # Conexión nativa. decode_responses=True convierte los bytes a Strings de Python automáticamente
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def vaciar_base_de_datos(self):
        self.client.flushdb()
        print("[*] Memoria RAM de Redis vaciada para demostración limpia.")

    def poblar_300_registros(self):
        """Genera exactamente 300 Claves (Keys) consistentes en Redis mediante Faker"""
        self.vaciar_base_de_datos()
        
        # 1. Generar 100 Carritos de Compras activos (100 Keys)
        print("[*] Creando 100 carritos de compra (Estructura: HASH)...")
        for i in range(1, 101):
            key_carrito = f"cart:u_{i}"
            # Cada carrito tiene entre 1 y 3 productos distintos adentro
            for _ in range(random.randint(1, 3)):
                id_producto = f"p_{random.randint(1, 50)}"
                cantidad = random.randint(1, 2)
                self.client.hset(key_carrito, id_producto, cantidad)

        # 2. Generar 200 Sesiones de Usuarios concurrentes (200 Keys)
        print("[*] Creando 200 sesiones activas con Faker (Estructura: HASH con TTL)...")
        roles_posibles = ["cliente", "cliente", "cliente", "admin"] # Simulación estadística de roles
        for i in range(1, 201):
            key_sesion = f"session:token_{i}"
            datos_sesion = {
                "id_usuario": f"u_{i}",
                "alias": fake.user_name(),
                "rol": random.choice(roles_posibles),
                "ip_origen": fake.ipv4()
            }
            # Guardamos el diccionario completo en el Hash
            self.client.hset(key_sesion, mapping=datos_sesion)
            # Definimos un TTL aleatorio entre 10 y 30 minutos (en segundos)
            self.client.expire(key_sesion, random.randint(600, 1800))

        # Validación final del tamaño
        print("\n" + "="*50)
        print(f" [ÉXITO] Ingesta completada con Faker.")
        print(f" -> Carritos creados: 100")
        print(f" -> Sesiones creadas: 200")
        print(f" -> TOTAL DE KEYS VERIFICADAS EN REDIS (dbsize): {self.client.dbsize()}")
        print("="*50)

    # =================================================================
    # FUNCIONES OPERATIVAS PARA LA DEMOSTRACIÓN (CARRITO)
    # =================================================================
    def agregar_al_carrito(self, user_id, prod_id, cantidad=1):
        # HINCRBY incrementa si existe, o lo crea desde 0 si no existía.
        self.client.hincrby(f"cart:{user_id}", prod_id, cantidad)
        print(f"[CARRITO] Se sumó {cantidad} unidad/es de '{prod_id}' al carrito de '{user_id}' en RAM.")

    def ver_carrito(self, user_id):
        carrito = self.client.hgetall(f"cart:{user_id}")
        print(f"\n--- CONTENIDO DEL CARRITO DEL USUARIO ({user_id}) ---")
        if not carrito:
            print("  (El carrito se encuentra vacío)")
            return
        for prod, cant in carrito.items():
            print(f"  • ID Producto: {prod} | Cantidad en Carrito: {cant}")

    # =================================================================
    # FUNCIONES OPERATIVAS PARA LA DEMOSTRACIÓN (SESIONES / PERMISOS)
    # =================================================================
    def registrar_login_demo(self, token, usuario, rol):
        key = f"session:{token}"
        self.client.hset(key, mapping={"id_usuario": "u_999", "alias": usuario, "rol": rol})
        self.client.expire(key, 120) # 2 minutos de vida para probar en vivo
        print(f"[SESIÓN] Login exitoso. Guardado token '{token}' para '{usuario}' [{rol}] en Redis.")

    def validar_permisos_pantalla(self, token, requiere_admin=False):
        key = f"session:{token}"
        sesion = self.client.hgetall(key)
        
        if not sesion:
            print("\n[🚫 ACCESO DENEGADO] Token inválido o sesión expirada en Redis. Redirigiendo a Login.")
            return False
            
        if requiere_admin and sesion.get("rol") != "admin":
            print(f"\n[🚫 ACCESO DENEGADO] El usuario '{sesion.get('alias')}' tiene rol CLIENTE. Pantalla bloqueada.")
            return False
            
        print(f"\n[✅ ACCESO AUTORIZADO] Hola {sesion.get('alias')} ({sesion.get('rol').upper()}). Cargando pantalla...")
        return True

# =================================================================
# INTERFAZ POR TERMINAL
# =================================================================
def menu_interactivo():
    r = ControladorRedisMarketplace()
    TOKEN_CLIENTE = "tk_client_demo"
    TOKEN_ADMIN = "tk_admin_demo"

    while True:
        print("\n" + "="*50)
        print("     SISTEMA EN MEMORIA REDIS - PANEL DEL TP       ")
        print("="*50)
        print("1. Ejecutar Ingesta Masiva Faker (300 Keys exactas)")
        print("2. Simular Logins (Escribir datos de sesión con TTL)")
        print("3. Intentar entrar a 'Panel Admin' (Validar Roles)")
        print("4. Agregar producto al Carrito (HINCRBY)")
        print("5. Ver estructura de mi Carrito (HGETALL)")
        print("6. Salir")
        
        opc = input("\nSeleccioná una opción (1-6): ")
        
        if opc == "1":
            r.poblar_300_registros()
        elif opc == "2":
            r.registrar_login_demo(TOKEN_CLIENTE, "Santi_Manga", "cliente")
            r.registrar_login_demo(TOKEN_ADMIN, "Profe_DBA", "admin")
        elif opc == "3":
            print("\n--- CASO A: Cliente común intentando ingresar a Panel Admin ---")
            r.validar_permisos_pantalla(TOKEN_CLIENTE, requiere_admin=True)
            print("\n--- CASO B: Administrador ingresando a Panel Admin ---")
            r.validar_permisos_pantalla(TOKEN_ADMIN, requiere_admin=True)
        elif opc == "4":
            pid = input("Ingresá el ID del producto (ej: p_berserk_5): ")
            r.agregar_al_carrito("u_demo", pid, 1)
        elif opc == "5":
            r.ver_carrito("u_demo")
        elif opc == "6":
            print("\nDesconectando de Redis. ¡El módulo quedó impecable!")
            break
        else:
            print("[ERROR] Opción inválida.")

if __name__ == "__main__":
    try:
        menu_interactivo()
    except Exception as e:
        print(f"\n[ERROR CRÍTICO]: No se pudo conectar a Redis: {e}")
        print("Asegurate de tener la instancia de Redis levantada en el puerto 6379.")