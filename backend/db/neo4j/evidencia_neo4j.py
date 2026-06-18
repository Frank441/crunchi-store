from neo4j import GraphDatabase

#pip install neo4j

class MotorRecomendacionNeo4j:
    def __init__(self, uri, user, password):
        # Conexión al clúster de Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def recomendar_tambien_compraron(self, id_producto):
        """
        Aplica Filtrado Colaborativo Item-Based:
        Busca qué otros productos compraron los usuarios que adquirieron el producto actual.
        """
        query = """
        MATCH (p:Producto {id: $id_prod})<-[:COMPRO]-(u:Usuario)-[:COMPRO]->(recom:Producto)
        WHERE p <> recom
        RETURN recom.titulo AS titulo, count(u) AS frecuencia
        ORDER BY frecuencia DESC
        LIMIT 5
        """
        # Ejecutamos la consulta abriendo una sesión de lectura (buena práctica)
        with self.driver.session() as session:
            resultados = session.execute_read(self._ejecutar_y_formatear, query, id_producto)
            return resultados

    @staticmethod
    def _ejecutar_y_formatear(tx, query, id_producto):
        result = tx.run(query, id_prod=id_producto)
        return [{"titulo": record["titulo"], "frecuencia": record["frecuencia"]} for record in result]

# === USO PARA MOSTRAR EN LA DEFENSA ===
if __name__ == "__main__":
    # Credenciales por defecto de Neo4j local o en Docker
    motor = MotorRecomendacionNeo4j("bolt://localhost:7687", "neo4j", "password123")
    
    print("\n--- MOTOR DE RECOMENDACIONES: FILTRADO COLABORATIVO ---")
    producto_viendo = 7 # Supongamos que es el ID de 'Berserk Vol. 1'
    print(f"Buscando recomendaciones para quienes compraron el producto '{producto_viendo}'...\n")
    
    recomendaciones = motor.recomendar_tambien_compraron(producto_viendo)
    
    for rank, item in enumerate(recomendaciones, 1):
        print(f"{rank}. {item['titulo']} (Comprado por {item['frecuencia']} usuarios en común)")

    motor.close()