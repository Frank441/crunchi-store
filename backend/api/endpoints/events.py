from fastapi import HTTPException, status
from datetime import datetime
from db.cassandra import cassandra as cassandra_db
from api.main import app
from api.classes import EventoInsertInput



@app.post("/cassandra/evento", status_code=status.HTTP_201_CREATED)
def insertar_evento_manual(datos: EventoInsertInput):
    """
    Simulación de envío de eventos desde el Front.
    Inserta la información de forma duplicada en 'eventos_por_usuario' y 'eventos_por_producto'
    para asegurar que el panel de analítica disponga de todos los datos en O(1).
    """
    session = cassandra_db.get_session()
    
    # Si el frontend no define una fecha_hora específica, tomamos el instante actual
    fecha_exacta = datos.fecha_hora if datos.fecha_hora else datetime.now()

    # Preparamos las sentencias para asegurar consistencia y performance
    query_usuario = """
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, evento, id_producto)
        VALUES (?, ?, ?, ?)
    """
    query_producto = """
        INSERT INTO eventos_por_producto (id_producto, evento, fecha_hora, id_usuario)
        VALUES (?, ?, ?, ?)
    """

    try:
        # Inserción obligatoria en ambas estructuras (Query-Driven Architecture)
        session.execute(query_usuario, (datos.id_usuario, fecha_exacta, datos.evento, datos.id_producto))
        session.execute(query_producto, (datos.id_producto, datos.evento, fecha_exacta, datos.id_usuario))
        
        return {
            "status": "success",
            "mensaje": "Evento registrado exitosamente en ambas tablas de Cassandra.",
            "datos_insertados": {
                "id_usuario": datos.id_usuario,
                "id_producto": datos.id_producto,
                "evento": datos.evento,
                "fecha_hora": fecha_exacta
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escribir en Cassandra: {str(e)}"
        )