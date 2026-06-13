from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from api.classes import EventoInsertInput
from db.cassandra import cassandra as cassandra_db

router = APIRouter(tags=["eventos"])


@router.post("/cassandra/evento", status_code=status.HTTP_201_CREATED)
def insertar_evento_manual(datos: EventoInsertInput):
    """
    Registra un evento de navegación/compra desde el frontend.

    Inserta en paralelo en 'eventos_por_usuario' y 'eventos_por_producto'
    para mantener la desnormalización que permite lecturas O(1) en ambos
    paneles de analítica (Query-Driven Architecture).

    Los IDs son enteros (igual que en MongoDB) para garantizar coherencia
    entre motores.
    """
    session = cassandra_db.get_session()

    fecha_exacta = datos.fecha_hora if datos.fecha_hora else datetime.now()

    stmt_usuario = session.prepare("""
        INSERT INTO eventos_por_usuario (id_usuario, fecha_hora, evento, id_producto)
        VALUES (?, ?, ?, ?)
    """)

    stmt_producto = session.prepare("""
        INSERT INTO eventos_por_producto (id_producto, evento, fecha_hora, id_usuario)
        VALUES (?, ?, ?, ?)
    """)

    try:
        session.execute(stmt_usuario, (datos.id_usuario, fecha_exacta, datos.evento, datos.id_producto))
        session.execute(stmt_producto, (datos.id_producto, datos.evento, fecha_exacta, datos.id_usuario))

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