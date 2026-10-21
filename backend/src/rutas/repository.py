from datetime import date, time

from sqlalchemy import text
from sqlalchemy.orm import Session

_COLUMNAS_RUTA = (
    "r.ruta_id, r.lote_id, r.fecha_jornada, r.estado, r.hora_salida, r.hora_regreso, r.distancia_km, r.tiempo_min, "
    "r.reemplaza_ruta_id, v.vehiculo_id, v.placa, v.tipo, c.conductor_id, c.nombre AS conductor_nombre, "
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
            if d["reemplaza_ruta_id"] is not None:
                d["reemplaza_ruta_id"] = str(d["reemplaza_ruta_id"])
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
                "SELECT rp.ruta_id, rp.orden_entrega, rp.pedido_id, rp.hora_estimada, rp.minutos_retraso, rp.estado_entrega, "
                "p.descripcion, p.peso_kg, p.prioridad, p.latitud, p.longitud, p.estado AS pedido_estado, cl.nombre AS cliente "
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

    # ------------------------------------------------------------------ re-optimización (HU-012)
    def rutas_activas(self, fecha: date) -> list[dict]:
        """Rutas confirmadas o en ejecución de la fecha, con los datos de su vehículo y su conductor."""
        rows = self.session.execute(
            text(
                "SELECT r.ruta_id, r.estado, r.hora_salida, v.vehiculo_id, v.placa, v.tipo, v.capacidad_kg, v.consumo_km_l, "
                "v.factor_emision_co2, v.estado AS vehiculo_estado, c.conductor_id, c.categoria_licencia, c.licencia_vence, "
                "c.horario_inicio, c.horario_fin, c.disponible "
                "FROM rutas r JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id JOIN conductores c ON c.conductor_id = r.conductor_id "
                "WHERE r.fecha_jornada = :fecha AND r.estado IN ('CONFIRMADA', 'EN_EJECUCION') ORDER BY v.placa"
            ),
            {"fecha": fecha},
        ).all()
        salida = []
        for r in rows:
            d = dict(r._mapping)
            for clave in ("ruta_id", "vehiculo_id", "conductor_id"):
                d[clave] = str(d[clave])
            salida.append(d)
        return salida

    def paradas_para_reoptimizar(self, ruta_ids: list[str]) -> dict[str, list[dict]]:
        """Paradas de las rutas con el estado de su entrega y los datos del pedido que necesita el motor."""
        if not ruta_ids:
            return {}
        rows = self.session.execute(
            text(
                "SELECT rp.ruta_id, rp.pedido_id, rp.orden_entrega, rp.estado_entrega, rp.entregado_en, p.estado AS pedido_estado, "
                "p.peso_kg, p.prioridad, p.latitud, p.longitud, p.ventana_inicio, p.ventana_fin "
                "FROM ruta_pedidos rp JOIN pedidos p ON p.pedido_id = rp.pedido_id "
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

    def borrar_borradores_de_reemplazo(self, ruta_ids: list[str]) -> int:
        """Elimina los borradores de re-optimización anteriores de esas rutas en curso."""
        return self.session.execute(
            text("DELETE FROM rutas WHERE reemplaza_ruta_id = ANY(CAST(:ids AS uuid[])) AND estado = 'PLANIFICADA'"), {"ids": ruta_ids}
        ).rowcount

    def crear_rutas_de_reemplazo(self, filas: list[dict]) -> None:
        self._insertar_filas(
            "rutas",
            ("ruta_id", "lote_id", "vehiculo_id", "conductor_id", "fecha_jornada", "hora_salida", "hora_regreso", "distancia_km",
             "tiempo_min", "reemplaza_ruta_id"),
            filas,
        )

    def reemplazos_del_lote(self, lote_id: str) -> list[dict]:
        """Borradores del lote que reemplazan a una ruta en curso (vacío si el lote es una generación normal)."""
        rows = self.session.execute(
            text(
                "SELECT ruta_id, reemplaza_ruta_id, hora_regreso, distancia_km, tiempo_min FROM rutas "
                "WHERE lote_id = :lote AND reemplaza_ruta_id IS NOT NULL ORDER BY ruta_id"
            ),
            {"lote": lote_id},
        ).all()
        return [
            dict(r._mapping) | {"ruta_id": str(r[0]), "reemplaza_ruta_id": str(r[1])} for r in rows
        ]

    def bloquear_rutas_originales(self, ids: list[str]) -> list[dict]:
        rows = self.session.execute(
            text("SELECT ruta_id, estado FROM rutas WHERE ruta_id = ANY(CAST(:ids AS uuid[])) ORDER BY ruta_id FOR UPDATE"), {"ids": ids}
        ).all()
        return [{"ruta_id": str(r[0]), "estado": r[1]} for r in rows]

    def pedidos_invalidos_del_reemplazo(self, lote_id: str) -> list[str]:
        """Pedidos de los borradores que ya no se pueden asignar: no están pendientes ni siguen asignados a una de
        las rutas en curso que se reemplazan (p. ej. se cancelaron después de re-optimizar). Bloquea sus filas."""
        rows = self.session.execute(
            text(
                "SELECT p.pedido_id FROM ruta_pedidos rp JOIN rutas d ON d.ruta_id = rp.ruta_id "
                "JOIN pedidos p ON p.pedido_id = rp.pedido_id "
                "WHERE d.lote_id = :lote AND d.reemplaza_ruta_id IS NOT NULL AND NOT (p.estado = 'PENDIENTE' OR "
                "(p.estado = 'ASIGNADO' AND EXISTS (SELECT 1 FROM ruta_pedidos o WHERE o.pedido_id = p.pedido_id "
                "AND o.estado_entrega = 'PENDIENTE' AND o.ruta_id IN "
                "(SELECT reemplaza_ruta_id FROM rutas WHERE lote_id = :lote)))) "
                "ORDER BY p.pedido_id FOR UPDATE OF p"
            ),
            {"lote": lote_id},
        ).all()
        return [str(r[0]) for r in rows]

    def confirmar_reemplazo(self, lote_id: str, reemplazos: list[dict]) -> tuple[int, int]:
        """Pasa las paradas pendientes de cada ruta en curso a las del borrador de su re-optimización.
        Devuelve (rutas actualizadas, pedidos nuevos asignados)."""
        nuevos = self.session.execute(
            text(
                "UPDATE pedidos SET estado = 'ASIGNADO' WHERE estado = 'PENDIENTE' AND pedido_id IN "
                "(SELECT rp.pedido_id FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id WHERE r.lote_id = :lote)"
            ),
            {"lote": lote_id},
        ).rowcount
        originales = [r["reemplaza_ruta_id"] for r in reemplazos]
        # Primero se vacían las paradas pendientes de todas las rutas: un pedido puede cambiar de ruta
        self.session.execute(
            text("DELETE FROM ruta_pedidos WHERE ruta_id = ANY(CAST(:ids AS uuid[])) AND estado_entrega = 'PENDIENTE'"), {"ids": originales}
        )
        for r in reemplazos:
            original, borrador = r["reemplaza_ruta_id"], r["ruta_id"]
            hechas = self.session.execute(
                text("SELECT coalesce(max(orden_entrega), 0) FROM ruta_pedidos WHERE ruta_id = :ruta"), {"ruta": original}
            ).scalar_one()
            self.session.execute(
                text("UPDATE ruta_pedidos SET ruta_id = :original, orden_entrega = orden_entrega + :hechas WHERE ruta_id = :borrador"),
                {"original": original, "borrador": borrador, "hechas": hechas},
            )
            self.session.execute(
                text(
                    "DELETE FROM metricas_sostenibilidad WHERE ruta_id = :original AND "
                    "EXISTS (SELECT 1 FROM metricas_sostenibilidad WHERE ruta_id = :borrador)"
                ),
                {"original": original, "borrador": borrador},
            )
            self.session.execute(
                text("UPDATE metricas_sostenibilidad SET ruta_id = :original WHERE ruta_id = :borrador"),
                {"original": original, "borrador": borrador},
            )
            quedan = self.session.execute(
                text("SELECT count(*) FROM ruta_pedidos WHERE ruta_id = :ruta AND estado_entrega = 'PENDIENTE'"), {"ruta": original}
            ).scalar_one()
            estado = None
            if quedan == 0:  # sin paradas por atender: terminó si ya atendió alguna, y si no se cancela
                estado = "COMPLETADA" if hechas else "CANCELADA"
            self.session.execute(
                text(
                    "UPDATE rutas SET hora_regreso = :hr, distancia_km = :dk, tiempo_min = :tm, estado = coalesce(:estado, estado) "
                    "WHERE ruta_id = :original"
                ),
                {"hr": r["hora_regreso"], "dk": r["distancia_km"], "tm": r["tiempo_min"], "estado": estado, "original": original},
            )
            self.session.execute(text("DELETE FROM rutas WHERE ruta_id = :borrador"), {"borrador": borrador})
        return len(reemplazos), nuevos

    # ------------------------------------------------------------------ entregas (HU-012)
    def obtener_parada(self, ruta_id: str, pedido_id: str) -> dict | None:
        row = self.session.execute(
            text(
                "SELECT rp.estado_entrega, r.estado AS estado_ruta FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id "
                "WHERE rp.ruta_id = :ruta AND rp.pedido_id = :pedido"
            ),
            {"ruta": ruta_id, "pedido": pedido_id},
        ).one_or_none()
        return dict(row._mapping) if row else None

    def marcar_entrega(self, ruta_id: str, pedido_id: str, estado: str) -> bool:
        """Marca la parada solo si sigue pendiente y su ruta está activa. Devuelve si hubo cambio."""
        return bool(
            self.session.execute(
                text(
                    "UPDATE ruta_pedidos rp SET estado_entrega = :estado, entregado_en = CURRENT_TIMESTAMP FROM rutas r "
                    "WHERE rp.ruta_id = r.ruta_id AND rp.ruta_id = :ruta AND rp.pedido_id = :pedido "
                    "AND rp.estado_entrega = 'PENDIENTE' AND r.estado IN ('CONFIRMADA', 'EN_EJECUCION')"
                ),
                {"estado": estado, "ruta": ruta_id, "pedido": pedido_id},
            ).rowcount
        )

    def marcar_pedido_entregado(self, pedido_id: str) -> None:
        self.session.execute(
            text("UPDATE pedidos SET estado = 'ENTREGADO' WHERE pedido_id = :pedido AND estado IN ('ASIGNADO', 'EN_CAMINO')"),
            {"pedido": pedido_id},
        )

    def actualizar_estado_de_ruta(self, ruta_id: str) -> str:
        """EN_EJECUCION mientras queden paradas por atender (sin contar pedidos cancelados); COMPLETADA al terminar."""
        pendientes = self.session.execute(
            text(
                "SELECT count(*) FROM ruta_pedidos rp JOIN pedidos p ON p.pedido_id = rp.pedido_id "
                "WHERE rp.ruta_id = :ruta AND rp.estado_entrega = 'PENDIENTE' AND p.estado <> 'CANCELADO'"
            ),
            {"ruta": ruta_id},
        ).scalar_one()
        estado = "EN_EJECUCION" if pendientes else "COMPLETADA"
        self.session.execute(text("UPDATE rutas SET estado = :estado WHERE ruta_id = :ruta"), {"estado": estado, "ruta": ruta_id})
        return estado

    # ------------------------------------------------------------------ incidentes de tráfico (RN-012)
    _COLUMNAS_INCIDENTE = "incidente_id, calle, factor, descripcion, activo, creado_en, resuelto_en"

    def _incidente(self, row) -> dict:
        d = dict(row._mapping)
        d["incidente_id"], d["factor"] = str(d["incidente_id"]), float(d["factor"])
        return d

    def crear_incidente(self, usuario_id: str, calle: str, factor: float, descripcion: str | None) -> dict:
        row = self.session.execute(
            text(
                "INSERT INTO incidentes_trafico (calle, factor, descripcion, registrado_por) "  # nosec B608
                f"VALUES (:calle, :factor, :descripcion, :usuario) RETURNING {self._COLUMNAS_INCIDENTE}"
            ),
            {"calle": calle, "factor": factor, "descripcion": descripcion, "usuario": usuario_id},
        ).one()
        return self._incidente(row)

    def incidentes(self, solo_activos: bool = True) -> list[dict]:
        condicion = "WHERE activo" if solo_activos else ""
        rows = self.session.execute(
            text(f"SELECT {self._COLUMNAS_INCIDENTE} FROM incidentes_trafico {condicion} ORDER BY creado_en DESC")  # nosec B608
        ).all()
        return [self._incidente(r) for r in rows]

    def resolver_incidente(self, incidente_id: str) -> dict | None:
        row = self.session.execute(
            text(
                "UPDATE incidentes_trafico SET activo = FALSE, resuelto_en = CURRENT_TIMESTAMP "  # nosec B608
                f"WHERE incidente_id = :id AND activo RETURNING {self._COLUMNAS_INCIDENTE}"
            ),
            {"id": incidente_id},
        ).one_or_none()
        return self._incidente(row) if row else None

    # ------------------------------------------------------------------ vista del conductor (HU-014)
    def conductor_del_usuario(self, usuario_id: str, correo: str | None) -> dict | None:
        """El conductor de este usuario. Si todavía no está vinculado, lo vincula por correo: el conductor cuyo correo
        coincide (sin distinguir mayúsculas) con el de la cuenta y que no tiene usuario. `nuevo` indica ese caso."""
        fila = self.session.execute(
            text("SELECT conductor_id, nombre FROM conductores WHERE usuario_id = :u"), {"u": usuario_id}
        ).one_or_none()
        nuevo = False
        if fila is None and correo:
            fila = self.session.execute(
                text(
                    "UPDATE conductores SET usuario_id = :u WHERE conductor_id = (SELECT conductor_id FROM conductores "
                    "WHERE usuario_id IS NULL AND lower(correo) = lower(:c) ORDER BY creado_en, conductor_id LIMIT 1) "
                    "RETURNING conductor_id, nombre"
                ),
                {"u": usuario_id, "c": correo},
            ).one_or_none()
            nuevo = fila is not None
        return {"conductor_id": str(fila[0]), "nombre": fila[1], "nuevo": nuevo} if fila else None

    def rutas_del_conductor(self, conductor_id: str, fecha: date) -> list[dict]:
        """Rutas del conductor en esa fecha que ya puede ver: confirmadas, en ejecución o completadas (nunca borradores)."""
        return self._rutas(
            "r.conductor_id = :conductor AND r.fecha_jornada = :fecha AND r.estado IN ('CONFIRMADA', 'EN_EJECUCION', 'COMPLETADA')",
            {"conductor": conductor_id, "fecha": fecha},
        )
