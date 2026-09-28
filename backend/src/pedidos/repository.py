from sqlalchemy import text
from sqlalchemy.orm import Session

_COLUMNAS = (
    "pedido_id, cliente_id, descripcion, peso_kg, volumen_m3, prioridad, "
    "latitud, longitud, ventana_inicio, ventana_fin, estado, creado_en"
)


class RepositorioPedidos:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, datos: dict) -> str:
        row = self.session.execute(
            text(
                "INSERT INTO pedidos "
                "(cliente_id, descripcion, peso_kg, volumen_m3, prioridad, latitud, longitud, "
                " ventana_inicio, ventana_fin) "
                "VALUES (:cliente_id, :descripcion, :peso_kg, :volumen_m3, :prioridad, "
                ":latitud, :longitud, :ventana_inicio, :ventana_fin) "
                "RETURNING pedido_id"
            ),
            datos,
        ).one()
        return str(row[0])

    def obtener(self, pedido_id: str) -> dict | None:
        row = self.session.execute(
            text(f"SELECT {_COLUMNAS} FROM pedidos WHERE pedido_id = :pid"), {"pid": pedido_id}
        ).one_or_none()
        return self._a_dict(row) if row else None

    def cambiar_estado(self, pedido_id: str, nuevo_estado: str, desde_estados: list[str]) -> dict | None:
        """Actualiza el estado solo si el estado actual está en `desde_estados` (transición válida)."""
        row = self.session.execute(
            text(
                f"UPDATE pedidos SET estado = :nuevo WHERE pedido_id = :pid "
                f"AND estado = ANY(:desde) RETURNING {_COLUMNAS}"
            ),
            {"nuevo": nuevo_estado, "pid": pedido_id, "desde": desde_estados},
        ).one_or_none()
        return self._a_dict(row) if row else None

    def listar(self, estado: str | None, prioridad: str | None) -> list[dict]:
        condiciones, parametros = [], {}
        if estado:
            condiciones.append("estado = :estado")
            parametros["estado"] = estado
        if prioridad:
            condiciones.append("prioridad = :prioridad")
            parametros["prioridad"] = prioridad
        where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
        rows = self.session.execute(
            text(f"SELECT {_COLUMNAS} FROM pedidos {where} ORDER BY creado_en DESC"), parametros
        ).all()
        return [self._a_dict(r) for r in rows]

    @staticmethod
    def _a_dict(row) -> dict:
        return {
            "pedido_id": str(row[0]),
            "cliente_id": str(row[1]),
            "descripcion": row[2],
            "peso_kg": row[3],
            "volumen_m3": row[4],
            "prioridad": row[5],
            "latitud": row[6],
            "longitud": row[7],
            "ventana_inicio": row[8],
            "ventana_fin": row[9],
            "estado": row[10],
            "creado_en": row[11],
        }
