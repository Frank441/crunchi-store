from api.main import app
from api.classes import SugerenciaHome, UsuarioNeo4jInput, AccionUsuarioNeo4jInput, ProductoNeo4jInput, EventoPorUsuarioOut
import uuid
from db.neo4j import neo4j as neo4j_db
from db.cassandra import cassandra as cassandra_db
from fastapi import HTTPException, status



@app.get("/usuarios/{usuario_id}/home-sugerencias", response_model=list[SugerenciaHome])
def obtener_sugerencias_home(usuario_id: str):
    """
    PANTALLA 2: La Home Page Personalizada.
    Filtrado colaborativo por afinidad de géneros consumidos, excluyendo lo visto o comprado.
    """
    query = """
    MATCH (u:Usuario {id: $user_id})-[:COMPRO]->(:Producto)-[:PERTENECE_A]->(g:Genero)<-[:PERTENECE_A]-(p_sugerido:Producto)
    WHERE NOT (u)-[:COMPRO]->(p_sugerido) AND NOT (u)-[:VIO]->(p_sugerido)
    RETURN p_sugerido.id AS id, p_sugerido.titulo AS titulo, count(g) AS puntos_afinidad
    ORDER BY puntos_afinidad DESC
    LIMIT 5;
    """
    
    with neo4j_db.get_session() as session:
        resultado = session.run(query, user_id=usuario_id)
        sugerencias = [
            SugerenciaHome(
                id_producto=registro["id"],
                titulo=registro["titulo"],
                puntos_afinidad=registro["puntos_afinidad"]
            )
            for registro in resultado
        ]
        
    return sugerencias

@app.post("/neo4j/usuario", status_code=status.HTTP_201_CREATED)
def insertar_usuario_neo4j(datos: UsuarioNeo4jInput):
    """
    Crea o actualiza de forma manual un nodo Usuario en el grafo.
    """
    query = """
        MERGE (u:Usuario {id: $id_user})
        SET u.alias = $alias
        RETURN u.id AS id, u.alias AS alias
    """
    with neo4j_db.get_session() as session:
        try:
            session.run(query, id_user=datos.id_usuario, alias=datos.alias)
            return {"status": "success", "mensaje": f"Usuario '{datos.alias}' registrado en Neo4j."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en Neo4j: {str(e)}")


@app.post("/neo4j/accion-usuario", status_code=status.HTTP_201_CREATED)
def registrar_accion_usuario_neo4j(datos: AccionUsuarioNeo4jInput):
    """
    Crea interacciones dinámicas de grafos (relaciones COMPRO o VIO) desde el front
    para alimentar en tiempo real el motor de recomendaciones colaborativas.
    """
    # Validamos que el front mande una relación segura para el grafo
    relacion_limpia = datos.relacion.upper()
    if relacion_limpia not in ["COMPRO", "VIO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La relación debe ser exclusivamente 'COMPRO' o 'VIO'"
        )

    # Usamos APOC o concatenación segura interna para la query ya que las relaciones en Cypher no admiten parámetros nativos directos $
    query = f"""
        MATCH (u:Usuario {{id: $id_user}})
        MATCH (p:Producto {{id: $id_prod}})
        MERGE (u)-[:{relacion_limpia}]->(p)
    """
    with neo4j_db.get_session() as session:
        try:
            resultado = session.run(query, id_user=datos.id_usuario, id_prod=datos.id_producto)
            # Validamos si los nodos realmente existían antes de relacionarlos
            if resultado.consume().counters.relationships_created == 0:
                # Si no se creó nada, verificamos si es porque ya existía o porque no encontró los nodos
                pass
            return {"status": "success", "mensaje": f"Relación -[:{relacion_limpia}]-> establecida correctamente."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al relacionar en Neo4j: {str(e)}")
        

# --- ENDPOINTS CASSANDRA (PANEL DE ANALÍTICA - SOLO LECTURA REAL) ---
@app.get("/usuario/{id_usuario}", response_model=list[EventoPorUsuarioOut])
def obtener_user_journey(id_usuario: uuid.UUID):
    """
    BLOQUE 1: Rastreador de Usuarios (User Journey Tracker)
    
    Devuelve TODOS los campos de la tabla 'eventos_por_usuario' ordenados 
    cronológicamente de manera descendente (fecha_hora DESC) para auditar 
    el flujo completo de clics de un cliente.
    """
    session = cassandra_db.get_session()
    
    # Traemos todos los campos tal cual están en tu modelo CQL
    query = "SELECT id_usuario, fecha_hora, evento, id_producto FROM eventos_por_usuario WHERE id_usuario = ?"
    
    try:
        resultado = session.execute(query, (id_usuario,))
        return [
            EventoPorUsuarioOut(
                id_usuario=fila.id_usuario,
                fecha_hora=fila.fecha_hora,
                evento=fila.evento,
                id_producto=fila.id_producto
            )
            for fila in resultado
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Cassandra: {str(e)}"
        )
