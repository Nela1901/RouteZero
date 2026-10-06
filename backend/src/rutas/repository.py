from datetime import date, time

from sqlalchemy import text
from sqlalchemy.orm import Session

_COLUMNAS_RUTA = (
    "r.ruta_id, r.lote_id, r.fecha_jornada, r.estado, r.hora_salida, r.hora_regreso, r.distancia_km, r.tiempo_min, "
    "v.vehiculo_id, v.placa, v.tipo, c.conductor_id, c.nombre AS conductor_nombre, "
    "m.emision_co2_kg, m.combustible_l, m.combustible_ahorrado_l, m.distancia_optimizada_km, m.cumplimiento_ventanas_pct, "
    "(SELECT count(*) FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) AS cantidad_paradas"
)
_JOIN_RUTA = (
    "FROM rutas r JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id "
    "JOIN conductores c ON c.conductor_id = r.conductor_id "
    "LEFT JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id"
)


class RepositorioRutas:
    """Acceso a `rutas`, `ruta_pedidos` y `metricas_sostenibilidad`, y lectura de los datos de entrada del
    motor (pedidos pendientes, vehículos y conductores). SQL parametrizado; nunca hace `commit()`.

    Las consultas de los datos de entrada son propias de este módulo (no importa el código de `pedidos`,
    `flota` ni `conductores`), como exige la independencia entre módulos."""

    def __init__(self, session: Session):
        self.session = session

    # ------------------------------------------------------------------ datos de entrada del motor
    def pedidos_pendientes(self) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT pedido_id, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin "
                "FROM pedidos WHERE estado = 'PENDIENTE' ORDER BY creado_en, pedido_id"
            )
        ).all()
        return [dict(r._mapping) | {"pedido_id": str(r[0])} for r in rows]

    def vehiculos_disponibles(self) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, estado "
                "FROM vehiculos WHERE estado = 'DISPONIBLE' ORDER BY placa"
            )
        ).all()
        return [dict(r._mapping) | {"vehiculo_id": str(r[0])} for r in rows]

    def conductores_elegibles(self, fecha: date) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT conductor_id, categoria_licencia, licencia_vence, horario_inicio, horario_fin, disponible "
                "FROM conductores WHERE disponible AND licencia_vence > :fecha ORDER BY dni"
            ),
            {"fecha": fecha},
        ).all()
        return [dict(r._mapping) | {"conductor_id": str(r[0])} for r in rows]

    # ------------------------------------------------------------------ escritura
    def bloquear_fecha(self, fecha: date) -> None:
        """Candado de la transacción para que dos generaciones de la misma fecha no se pisen."""
        self.session.execute(text("SELECT pg_advisory_xact_lock(hashtext(:clave))"), {"clave": f"rutas:{fecha.isoformat()}"})

    def borrar_borradores(self, fecha: date) -> int:
        """Elimina los borradores PLANIFICADA de la fecha; paradas y métricas caen en cascada."""
        resultado = self.session.execute(
            text("DELETE FROM rutas WHERE fecha_jornada = :fecha AND estado = 'PLANIFICADA'"), {"fecha": fecha}
        )
        return resultado.rowcount

    def crear_ruta(self, lote_id: str, vehiculo_id: str, conductor_id: str, fecha: date, hora_salida: time,
                   hora_regreso: time, distancia_km: float, tiempo_min: int) -> str:
        row = self.session.execute(
            text(
                "INSERT INTO rutas (lote_id, vehiculo_id, conductor_id, fecha_jornada, hora_salida, hora_regreso, "
                "distancia_km, tiempo_min) VALUES (:lote, :veh, :cond, :fecha, :salida, :regreso, :km, :min) "
                "RETURNING ruta_id"
            ),
            {"lote": lote_id, "veh": vehiculo_id, "cond": conductor_id, "fecha": fecha, "salida": hora_salida,
             "regreso": hora_regreso, "km": distancia_km, "min": tiempo_min},
        ).one()
        return str(row[0])

    def crear_parada(self, ruta_id: str, pedido_id: str, orden: int, hora_estimada: time, minutos_retraso: int) -> None:
        self.session.execute(
            text(
                "INSERT INTO ruta_pedidos (ruta_id, pedido_id, orden_entrega, hora_estimada, minutos_retraso) "
                "VALUES (:ruta, :pedido, :orden, :hora, :retraso)"
            ),
            {"ruta": ruta_id, "pedido": pedido_id, "orden": orden, "hora": hora_estimada, "retraso": minutos_retraso},
        )

    def crear_metricas(self, ruta_id: str, co2_kg: float, combustible_l: float, ahorrado_l: float,
                       distancia_km: float, cumplimiento_pct: float) -> None:
        self.session.execute(
            text(
                "INSERT INTO metricas_sostenibilidad (ruta_id, emision_co2_kg, combustible_l, combustible_ahorrado_l, "
                "distancia_optimizada_km, cumplimiento_ventanas_pct) VALUES (:ruta, :co2, :comb, :ahorro, :km, :pct)"
            ),
            {"ruta": ruta_id, "co2": co2_kg, "comb": combustible_l, "ahorro": ahorrado_l, "km": distancia_km, "pct": cumplimiento_pct},
        )

    # ------------------------------------------------------------------ lotes
    def estados_del_lote(self, lote_id: str) -> list[str]:
        rows = self.session.execute(text("SELECT estado FROM rutas WHERE lote_id = :lote"), {"lote": lote_id}).all()
        return [r[0] for r in rows]

    def bloquear_pedidos_del_lote(self, lote_id: str) -> list[dict]:
        """Bloquea las filas de los pedidos del lote hasta el final de la transacción (evita que un pedido se
        cancele mientras se confirma) y devuelve su estado actual."""
        rows = self.session.execute(
            text(
                "SELECT p.pedido_id, p.estado FROM pedidos p WHERE p.pedido_id IN "
                "(SELECT rp.pedido_id FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id WHERE r.lote_id = :lote) "
                "ORDER BY p.pedido_id FOR UPDATE"
            ),
            {"lote": lote_id},
        ).all()
        return [{"pedido_id": str(r[0]), "estado": r[1]} for r in rows]

    def confirmar_lote(self, lote_id: str) -> tuple[int, int]:
        """Rutas del lote a CONFIRMADA y sus pedidos a ASIGNADO. Devuelve (rutas, pedidos)."""
        pedidos = self.session.execute(
            text(
                "UPDATE pedidos SET estado = 'ASIGNADO' WHERE estado = 'PENDIENTE' AND pedido_id IN "
                "(SELECT rp.pedido_id FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id WHERE r.lote_id = :lote)"
            ),
            {"lote": lote_id},
        ).rowcount
        rutas = self.session.execute(
            text("UPDATE rutas SET estado = 'CONFIRMADA' WHERE lote_id = :lote AND estado = 'PLANIFICADA'"), {"lote": lote_id}
        ).rowcount
        return rutas, pedidos

    def borrar_lote(self, lote_id: str) -> int:
        return self.session.execute(text("DELETE FROM rutas WHERE lote_id = :lote"), {"lote": lote_id}).rowcount

    # ------------------------------------------------------------------ lectura
    def _rutas(self, condicion: str, parametros: dict) -> list[dict]:
        rows = self.session.execute(
            text(f"SELECT {_COLUMNAS_RUTA} {_JOIN_RUTA} WHERE {condicion} ORDER BY r.creado_en, v.placa"), parametros
        ).all()
        rutas = []
        for r in rows:
            d = dict(r._mapping)
            d["ruta_id"], d["lote_id"] = str(d["ruta_id"]), str(d["lote_id"])
            d["vehiculo_id"], d["conductor_id"] = str(d["vehiculo_id"]), str(d["conductor_id"])
            rutas.append(d)
        return rutas

    def rutas_de_la_fecha(self, fecha: date) -> list[dict]:
        return self._rutas("r.fecha_jornada = :fecha", {"fecha": fecha})

    def rutas_del_lote(self, lote_id: str) -> list[dict]:
        return self._rutas("r.lote_id = :lote", {"lote": lote_id})

    def obtener_ruta(self, ruta_id: str) -> dict | None:
        rutas = self._rutas("r.ruta_id = :ruta", {"ruta": ruta_id})
        return rutas[0] if rutas else None

    def paradas_de(self, ruta_ids: list[str]) -> dict[str, list[dict]]:
        if not ruta_ids:
            return {}
        rows = self.session.execute(
            text(
                "SELECT rp.ruta_id, rp.orden_entrega, rp.pedido_id, rp.hora_estimada, rp.minutos_retraso, "
                "p.descripcion, p.peso_kg, p.prioridad, p.latitud, p.longitud, cl.nombre AS cliente "
                "FROM ruta_pedidos rp JOIN pedidos p ON p.pedido_id = rp.pedido_id "
                "JOIN clientes cl ON cl.cliente_id = p.cliente_id "
                "WHERE rp.ruta_id = ANY(CAST(:ids AS uuid[])) ORDER BY rp.ruta_id, rp.orden_entrega"
            ),
            {"ids": ruta_ids},
        ).all()
        salida: dict[str, list[dict]] = {}
        for r in rows:
            d = dict(r._mapping)
            d["ruta_id"], d["pedido_id"] = str(d["ruta_id"]), str(d["pedido_id"])
            salida.setdefault(d["ruta_id"], []).append(d)
        return salida
