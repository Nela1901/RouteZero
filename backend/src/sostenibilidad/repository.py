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
                "JOIN (SELECT ruta_id, COUNT(*) AS paradas FROM ruta_pedidos GROUP BY ruta_id) p ON p.ruta_id = r.ruta_id "
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
