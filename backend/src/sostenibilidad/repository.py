from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

# Solo cuenta lo que se llevó a operación: un borrador (PLANIFICADA) o una ruta cancelada no es una jornada realizada.
_ESTADOS = ["CONFIRMADA", "EN_EJECUCION", "COMPLETADA"]


class RepositorioSostenibilidad:
    """Lecturas agregadas de `rutas`, `ruta_pedidos` y `metricas_sostenibilidad`, con SQL parametrizado. Este
    módulo no importa código de `rutas`: consulta las tablas por su cuenta."""

    def __init__(self, session: Session):
        self.session = session

    def totales(self, desde: date, hasta: date) -> dict:
        fila = self.session.execute(
            text(
                "SELECT COUNT(*) AS rutas, COALESCE(SUM(m.distancia_optimizada_km), 0) AS distancia_km, "
                "COALESCE(SUM(m.emision_co2_kg), 0) AS emision_co2_kg, COALESCE(SUM(m.combustible_l), 0) AS combustible_l, "
                "COALESCE(SUM(m.combustible_ahorrado_l), 0) AS combustible_ahorrado_l, "
                "COALESCE(SUM(m.cumplimiento_ventanas_pct * p.paradas), 0) AS ventanas_ponderadas, "
                "COALESCE(SUM(p.paradas), 0) AS paradas "
                "FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id "
                "JOIN LATERAL (SELECT COUNT(*) AS paradas FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) p ON TRUE "
                "WHERE r.estado = ANY(:estados) AND r.fecha_jornada BETWEEN :desde AND :hasta"
            ),
            {"estados": _ESTADOS, "desde": desde, "hasta": hasta},
        ).mappings().one()
        return dict(fila)

    def por_dia(self, desde: date, hasta: date) -> list[dict]:
        filas = self.session.execute(
            text(
                "SELECT r.fecha_jornada AS fecha, SUM(m.emision_co2_kg) AS emision_co2_kg, "
                "SUM(m.distancia_optimizada_km) AS distancia_km, SUM(m.combustible_ahorrado_l) AS combustible_ahorrado_l "
                "FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id "
                "WHERE r.estado = ANY(:estados) AND r.fecha_jornada BETWEEN :desde AND :hasta "
                "GROUP BY r.fecha_jornada ORDER BY r.fecha_jornada"
            ),
            {"estados": _ESTADOS, "desde": desde, "hasta": hasta},
        ).mappings().all()
        return [dict(f) for f in filas]

    def rutas_del_periodo(self, desde: date, hasta: date, limite: int) -> list[dict]:
        """Detalle por ruta para el reporte, de la más reciente a la más antigua (hasta `limite`)."""
        filas = self.session.execute(
            text(
                "SELECT r.fecha_jornada, v.placa, c.nombre AS conductor, p.paradas, m.distancia_optimizada_km AS distancia_km, "
                "m.emision_co2_kg, m.combustible_l, m.combustible_ahorrado_l "
                "FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id "
                "JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id JOIN conductores c ON c.conductor_id = r.conductor_id "
                "JOIN LATERAL (SELECT COUNT(*) AS paradas FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) p ON TRUE "
                "WHERE r.estado = ANY(:estados) AND r.fecha_jornada BETWEEN :desde AND :hasta "
                "ORDER BY r.fecha_jornada DESC, v.placa LIMIT :limite"
            ),
            {"estados": _ESTADOS, "desde": desde, "hasta": hasta, "limite": limite},
        ).mappings().all()
        return [dict(f) for f in filas]

    def flota_del_periodo(self, desde: date, hasta: date) -> list[dict]:
        """Vehículos en uso (no inactivos) o que rodaron en el periodo, con el combustible que gastaron."""
        filas = self.session.execute(
            text(
                "SELECT v.placa, v.tipo, v.precio_compra_soles, v.vida_util_anios, COALESCE(SUM(m.combustible_l), 0) AS combustible_l "
                "FROM vehiculos v LEFT JOIN rutas r ON r.vehiculo_id = v.vehiculo_id AND r.estado = ANY(:estados) "
                "AND r.fecha_jornada BETWEEN :desde AND :hasta "
                "LEFT JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id "
                "GROUP BY v.vehiculo_id, v.placa, v.tipo, v.precio_compra_soles, v.vida_util_anios, v.estado "
                "HAVING v.estado <> 'INACTIVO' OR COALESCE(SUM(m.combustible_l), 0) > 0 ORDER BY v.placa"
            ),
            {"estados": _ESTADOS, "desde": desde, "hasta": hasta},
        ).mappings().all()
        return [dict(f) for f in filas]

    def rutas_sin_completar(self, desde: date, hasta: date) -> int:
        """Rutas del periodo que siguen confirmadas o en ejecución: sus cifras todavía pueden cambiar."""
        return self.session.execute(
            text(
                "SELECT COUNT(*) FROM rutas WHERE estado IN ('CONFIRMADA', 'EN_EJECUCION') "
                "AND fecha_jornada BETWEEN :desde AND :hasta"
            ),
            {"desde": desde, "hasta": hasta},
        ).scalar_one()

    def entregas(self, desde: date, hasta: date) -> dict[str, int]:
        filas = self.session.execute(
            text(
                "SELECT rp.estado_entrega, COUNT(*) AS n FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id "
                "JOIN pedidos pe ON pe.pedido_id = rp.pedido_id "
                "WHERE r.estado = ANY(:estados) AND r.fecha_jornada BETWEEN :desde AND :hasta AND pe.estado <> 'CANCELADO' "
                "GROUP BY rp.estado_entrega"
            ),
            {"estados": _ESTADOS, "desde": desde, "hasta": hasta},
        ).all()
        return {estado: n for estado, n in filas}
