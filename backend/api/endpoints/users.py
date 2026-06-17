from api.classes import SugerenciaHome, UsuarioNeo4jInput, AccionUsuarioNeo4jInput, EventoPorUsuarioOut
from db.neo4j import neo4j as neo4j_db
from db.cassandra import cassandra as cassandra_db
from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["usuarios-analitica"])


# --- NEO4J ---

@router.get("/usuarios/{usuario_id}/home-sugerencias", response_model=list[SugerenciaHome])
def obtener_sugerencias_home(usuario_id: str):
    query = """
    MATCH (u:Usuario {id: $user_id})-[:COMPRO]->(:Producto)-[:PERTENECE_A]->(g:Genero)<-[:PERTENECE_A]-(p_sugerido:Producto)
    WHERE NOT (u)-[:COMPRO]->(p_sugerido) AND NOT (u)-[:VIO]->(p_sugerido)
    RETURN p_sugerido.id AS id, p_sugerido.titulo AS titulo, count(g) AS puntos_afinidad
    ORDER BY puntos_afinidad DESC
    LIMIT 5;
    """
    with neo4j_db.get_session() as session:
        resultado = session.run(query, user_id=usuario_id)
        return [
            SugerenciaHome(
                id_producto=registro["id"],
                titulo=registro["titulo"],
                puntos_afinidad=registro["puntos_afinidad"]
            )
            for registro in resultado
        ]


@router.post("/neo4j/usuario", status_code=status.HTTP_201_CREATED)
def insertar_usuario_neo4j(datos: UsuarioNeo4jInput):
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


@router.post("/neo4j/accion-usuario", status_code=status.HTTP_201_CREATED)
def registrar_accion_usuario_neo4j(datos: AccionUsuarioNeo4jInput):
    relacion_limpia = datos.relacion.upper()
    if relacion_limpia not in ["COMPRO", "VIO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La relación debe ser exclusivamente 'COMPRO' o 'VIO'"
        )
    query = f"""
        MATCH (u:Usuario {{id: $id_user}})
        MATCH (p:Producto {{id: $id_prod}})
        MERGE (u)-[:{relacion_limpia}]->(p)
    """
    with neo4j_db.get_session() as session:
        try:
            resultado = session.run(query, id_user=datos.id_usuario, id_prod=datos.id_producto)
            if resultado.consume().counters.relationships_created == 0:
                pass
            return {"status": "success", "mensaje": f"Relación -[:{relacion_limpia}]-> establecida correctamente."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al relacionar en Neo4j: {str(e)}")


# --- CASSANDRA ---

@router.get("/usuario/{id_usuario}/journey", response_model=list[EventoPorUsuarioOut])
def obtener_user_journey(id_usuario: int, limit: int = 20):
    session = cassandra_db.get_session()
    query = session.prepare("""
        SELECT id_usuario, fecha_hora, id_evento, evento, id_producto
        FROM eventos_por_usuario
        WHERE id_usuario = ?
        LIMIT ?
    """)
    try:
        resultado = session.execute(query, (id_usuario, limit))
        return [
            EventoPorUsuarioOut(
                id_usuario=fila.id_usuario,
                fecha_hora=fila.fecha_hora,
                id_evento=fila.id_evento,
                evento=fila.evento,
                id_producto=fila.id_producto,
            )
            for fila in resultado
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Cassandra: {str(e)}",
        )