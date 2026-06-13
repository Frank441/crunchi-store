from datetime import datetime

from cassandra.util import uuid_from_time
from fastapi import APIRouter, HTTPException, status

from api.classes import EventoInsertInput
from db.cassandra import cassandra as cassandra_db

router = APIRouter(tags=["eventos"])


@router.post("/cassandra/evento", status_code=status.HTTP_201_CREATED)
def insertar_evento_manual(datos: EventoInsertInput):
    session = cassandra_db.get_session()

    fecha_exacta = datos.fecha_hora if datos.fecha_hora else datetime.now()
    id_evento = uuid_from_time(fecha_exacta)

    stmt_usuario = session.prepare("""
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, id_evento, evento, id_producto)
        VALUES (?, ?, ?, ?, ?)
    """)

    stmt_producto = session.prepare("""
        INSERT INTO eventos_por_producto (id_producto, evento, id_evento, fecha_hora, id_usuario)
        VALUES (?, ?, ?, ?, ?)
    """)

    try:
        session.execute(stmt_usuario, (datos.id_usuario, fecha_exacta, id_evento, datos.evento, datos.id_producto))
        session.execute(stmt_producto, (datos.id_producto, datos.evento, id_evento, fecha_exacta, datos.id_usuario))

        return {
            "status": "success",
            "mensaje": "Evento registrado en ambas tablas de Cassandra.",
            "datos_insertados": {
                "id_usuario":  datos.id_usuario,
                "id_producto": datos.id_producto,
                "evento":      datos.evento,
                "fecha_hora":  fecha_exacta,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escribir en Cassandra: {str(e)}",
        )