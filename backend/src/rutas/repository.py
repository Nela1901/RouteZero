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

    def vehiculos_disponibles(self, fecha: date) -> list[dict]:
        """Vehículos en estado DISPONIBLE que no están ya comprometidos en una ruta confirmada de esa fecha."""
        rows = self.session.execute(
            text(
                "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, estado "
                "FROM vehiculos WHERE estado = 'DISPONIBLE' AND vehiculo_id NOT IN "
                "(SELECT vehiculo_id FROM rutas WHERE fecha_jornada = :fecha AND estado IN ('CONFIRMADA', 'EN_EJECUCION')) "
                "ORDER BY placa"
            ),
            {"fecha": fecha},
        ).all()
        return [dict(r._mapping) | {"vehiculo_id": str(r[0])} for r in rows]

    def conductores_elegibles(self, fecha: date) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT conductor_id, categoria_licencia, licencia_vence, horario_inicio, horario_fin, disponible "
                "FROM conductores WHERE disponible AND licencia_vence > :fecha AND conductor_id NOT IN "
                "(SELECT conductor_id FROM rutas WHERE fecha_jornada = :fecha AND estado IN ('CONFIRMADA', 'EN_EJECUCION')) "
                "ORDER BY dni"
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

    def _insertar_filas(self, tabla: str, columnas: tuple, filas: list[dict]) -> None:
        """Un solo INSERT con todas las filas. Insertar fila por fila cuesta un viaje a la base remota por
        fila (150 paradas tardaban ~16 s); en bloque son un par de viajes. Los nombres de tabla y columnas
        son constantes de este módulo; los valores siempre van como parámetros."""
        if not filas:
            return
        valores, parametros = [], {}
        for i, fila in enumerate(filas):
            valores.append("(" + ", ".join(f":{c}_{i}" for c in columnas) + ")")
            parametros.update({f"{c}_{i}": fila[c] for c in columnas})
        self.session.execute(
            text(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES {', '.join(valores)}"), parametros  # nosec B608
        )

    def crear_rutas(self, filas: list[dict]) -> None:
        """Cada fila trae su `ruta_id` (generado por el servicio) para poder enlazar paradas y métricas sin
        pedir los identificadores de vuelta."""
        self._insertar_filas(
            "rutas",
            ("ruta_id", "lote_id", "vehiculo_id", "conductor_id", "fecha_jornada", "hora_salida", "hora_regreso", "distancia_km", "tiempo_min"),
            filas,
        )

    def crear_paradas(self, filas: list[dict]) -> None:
        self._insertar_filas("ruta_pedidos", ("ruta_id", "pedido_id", "orden_entrega", "hora_estimada", "minutos_retraso"), filas)

    def crear_metricas(self, filas: list[dict]) -> None:
        self._insertar_filas(
            "metricas_sostenibilidad",
            ("ruta_id", "emision_co2_kg", "combustible_l", "combustible_ahorrado_l", "distancia_optimizada_km", "cumplimiento_ventanas_pct"),
            filas,
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
