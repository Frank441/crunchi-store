import redis
import random
from faker import Faker
#python -m pip install redis faker
fake = Faker('es_AR')

class ControladorRedisMarketplace:
    def __init__(self, host='localhost', port=6379, db=0):
        # decode_responses=True convierte automáticamente los bytes de Redis a Strings de Python
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
            for _ in range(random.randint(1, 3)):
                id_producto = f"p_{random.randint(1, 50)}"
                cantidad = random.randint(1, 2)
                self.client.hset(key_carrito, id_producto, quantity=cantidad)

        # 2. Generar 200 Sesiones de Usuarios concurrentes (200 Keys)
        print("[*] Creando 200 sesiones activas con Faker (Estructura: HASH con TTL)...")
        roles_posibles = ["cliente", "cliente", "cliente", "admin"]
        for i in range(1, 201):
            key_sesion = f"session:token_{i}"
            datos_sesion = {
                "id_usuario": f"u_{i}",
                "alias": fake.user_name(),
                "rol": random.choice(roles_posibles),
                "ip_origen": fake.ipv4()
            }
            self.client.hset(key_sesion, mapping=datos_sesion)
            # Definimos un TTL aleatorio entre 10 y 30 minutos (en segundos)
            self.client.expire(key_sesion, random.randint(600, 1800))

        # Validación final del tamaño solicitado para la entrega
        print("\n" + "="*50)
        print(f" [ÉXITO] Ingesta completada con Faker.")
        print(f" -> Carritos creados (Hashes): 100")
        print(f" -> Sesiones creadas (Hashes con TTL): 200")
        print(f" -> TOTAL DE KEYS EN REDIS (dbsize): {self.client.dbsize()}")
        print("="*50)

    # =================================================================
    # COMPONENTE A: PANEL DE SESIONES (USO 2)
    # =================================================================
    def obtener_panel_sesiones(self, limite=5):
        """Operación Avanzada: Lee las llaves de sesión y calcula su TTL en tiempo real"""
        # Buscamos las claves que cumplan el patrón de sesión
        claves_sesion = self.client.keys("session:*")
        print(f"\n=== PANTALLA: PANEL DE SESIONES ACTIVAS (Mostrando {min(limite, len(claves_sesion))} de {len(claves_sesion)}) ===")
        print(f"{'KEY/TOKEN':<20} | {'USUARIO':<15} | {'ROL':<10} | {'TIEMPO RESTANTE (TTL)':<20}")
        print("-" * 75)
        
        for key in claves_sesion[:limite]:
            datos = self.client.hgetall(key)
            ttl_segundos = self.client.ttl(key)
            
            # Formateamos el TTL a minutos y segundos reales
            minutos = ttl_segundos // 60
            segundos = ttl_segundos % 60
            tiempo_formateado = f"{minutos} min {segundos} seg"
            
            print(f"{key:<20} | {datos.get('alias', 'N/A'):<15} | {datos.get('rol', 'N/A').upper():<10} | {tiempo_formateado:<20}")

    def revocar_sesion_forzoso(self, token_id):
        """Comando DEL: Destruye la sesión en memoria RAM de forma inmediata"""
        key = f"session:{token_id}" if not token_id.startswith("session:") else token_id
        existe = self.client.exists(key)
        
        if existe:
            self.client.delete(key)
            print(f"\n[💥 REVOCAR] Se eliminó la clave '{key}' de Redis. El usuario fue desconectado.")
        else:
            print(f"\n[⚠️] La sesión '{key}' no existe o ya había expirado por su TTL.")

    # =================================================================
    # COMPONENTE B: OPERACIONES DEL CARRITO (USO 1)
    # =================================================================
    def agregar_al_carrito(self, user_id, prod_id, cantidad=1):
        # HINCRBY muta el valor numérico del campo de forma directa y segura
        self.client.hincrby(f"cart:{user_id}", prod_id, cantidad)
        print(f"[CARRITO] Se incrementó +{cantidad} el producto '{prod_id}' al usuario '{user_id}'.")

    def ver_carrito(self, user_id):
        carrito = self.client.hgetall(f"cart:{user_id}")
        print(f"\n--- VISTA DEL CARRITO (Usuario: {user_id}) ---")
        if not carrito:
            print("  El carrito no contiene productos en este momento.")
            return
        for prod, cant in carrito.items():
            print(f"  • ID Producto: {prod} -> Cantidad: {cant}")

# =================================================================
# MENÚ INTERACTIVO PARA LA DEFENSA ANTE LA CÁTEDRA
# =================================================================
def ejecutar_consola():
    r = ControladorRedisMarketplace()
    USER_TEST = "u_arquitecto"

    while True:
        print("\n" + "="*50)
        print("     SISTEMA EN MEMORIA REDIS - CONTROL DE DATOS   ")
        print("="*50)
        print("1. Ingesta Masiva Faker (Generar 300 Keys Exactas)")
        print("2. Ver Pantalla: Panel de Sesiones Activas (TTL)")
        print("3. Simular Acción de Soporte: Revocar Sesión (DEL)")
        print("4. Simular Interacción de Compra: Añadir al Carrito")
        print("5. Ver Pantalla: Mi Carrito Abierto (HGETALL)")
        print("6. Salir")
        
        opc = input("\nSeleccioná una opción de la demo (1-6): ")
        
        if opc == "1":
            r.poblar_300_registros()
        elif opc == "2":
            r.obtener_panel_sesiones()
        elif opc == "3":
            r.obtener_panel_sesiones(limite=3)
            token_a_borrar = input("\nIngresá el sufijo del token a revocar (ej: token_14): ")
            r.revocar_sesion_forzoso(token_a_borrar)
        elif opc == "4":
            pid = input("ID de Manga o Figura a agregar (ej: p_naruto_3): ")
            r.agregar_al_carrito(USER_TEST, pid, 1)
        elif opc == "5":
            r.ver_carrito(USER_TEST)
        elif opc == "6":
            print("\nMódulo de Redis finalizado con éxito.")
            break
        else:
            print("[⚠️] Opción inválida.")

if __name__ == "__main__":
    try:
        ejecutar_consola()
    except Exception as e:
        print(f"\n[CRITICAL ERROR]: Verificá que Redis esté corriendo localmente (puerto 6379): {e}")