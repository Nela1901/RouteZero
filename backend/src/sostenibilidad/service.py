import math
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status

from src.core.config import Settings, settings
from src.sostenibilidad.repository import RepositorioSostenibilidad

PERU = timezone(timedelta(hours=-5))  # Perú no usa horario de verano
MAXIMO_DIAS = 366

# RN-010: acciones que se sugieren cuando las emisiones del mes superan la meta.
ACCIONES_DE_REDUCCION = [
    "Regenerar y re-optimizar las rutas para acortar la distancia total recorrida.",
    "Reducir las jornadas o consolidar pedidos de zonas cercanas en una misma ruta.",
    "Asignar los pedidos a los vehículos de menor factor de emisión disponibles o migrar la flota a vehículos de menor emisión.",
]

# RN-011: tipos de alianza a explorar. Son propuestas: no hay convenios firmados con ninguna institución.
ALIANZAS_DE_REFORESTACION = [
    {
        "nombre": "Gobierno Regional de Junín y SERFOR",
        "descripcion": "Programas públicos de reforestación en la región; consultar áreas y especies nativas (queñua, aliso) para plantar.",
    },
    {
        "nombre": "Comunidades campesinas de la provincia de Huancayo",
        "descripcion": "Siembra y cuidado de plantones en tierras comunales, con seguimiento del número de árboles que sobreviven.",
    },
    {
        "nombre": "Universidades e institutos de la región",
        "descripcion": "Campañas de voluntariado y monitoreo del crecimiento de lo plantado, con apoyo académico.",
    },
]


def hoy_en_peru() -> date:
    return datetime.now(PERU).date()


def periodo_valido(desde: date | None, hasta: date | None, hoy: date) -> tuple[date, date]:
    """Sin fechas se toma el mes en curso. El periodo no puede ser invertido ni abarcar más de un año."""
    hasta = hasta or hoy
    desde = desde or hasta.replace(day=1)
    if desde > hasta:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "La fecha inicial no puede ser posterior a la final")
    if (hasta - desde).days >= MAXIMO_DIAS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "El periodo no puede superar un año")
    return desde, hasta


class ServicioSostenibilidad:
    def __init__(self, repo: RepositorioSostenibilidad, config: Settings = settings):
        self.repo = repo
        self.config = config

    def dashboard(self, desde: date | None, hasta: date | None) -> dict:
        desde, hasta = periodo_valido(desde, hasta, hoy_en_peru())
        t = self.repo.totales(desde, hasta)
        hay_datos = t["rutas"] > 0
        paradas = float(t["paradas"])
        entregas = self.repo.entregas(desde, hasta)
        ahorro_l = float(t["combustible_ahorrado_l"])
        return {
            "desde": desde, "hasta": hasta, "hay_datos": hay_datos,
            "mensaje": None if hay_datos else "No hay jornadas operativas registradas en el periodo seleccionado.",
            "totales": {
                "rutas": t["rutas"], "distancia_km": float(t["distancia_km"]), "emision_co2_kg": float(t["emision_co2_kg"]),
                "combustible_l": float(t["combustible_l"]), "combustible_ahorrado_l": ahorro_l,
                "ahorro_soles": ahorro_l * self.config.precio_combustible_soles_l,
                "cumplimiento_ventanas_pct": float(t["ventanas_ponderadas"]) / paradas if paradas else 0.0,
            },
            "entregas": {
                "entregadas": entregas.get("ENTREGADO", 0), "pendientes": entregas.get("PENDIENTE", 0),
                "fallidas": entregas.get("FALLIDO", 0),
            },
            "por_dia": [
                {"fecha": d["fecha"], "emision_co2_kg": float(d["emision_co2_kg"]), "distancia_km": float(d["distancia_km"]),
                 "combustible_ahorrado_l": float(d["combustible_ahorrado_l"])}
                for d in self.repo.por_dia(desde, hasta)
            ],
            "precio_combustible_soles_l": self.config.precio_combustible_soles_l,
        }

    def compensacion(self, desde: date | None, hasta: date | None) -> dict:
        """CO2 emitido en el periodo y árboles necesarios para compensarlo (RN-011). Además compara el mes de
        `hasta` con la meta mensual (RN-010) y, si la supera, sugiere acciones de reducción."""
        desde, hasta = periodo_valido(desde, hasta, hoy_en_peru())
        cfg = self.config
        emision = float(self.repo.totales(desde, hasta)["emision_co2_kg"])
        hay_datos = emision > 0
        inicio_mes = hasta.replace(day=1)
        emision_mes = emision if inicio_mes == desde else float(self.repo.totales(inicio_mes, hasta)["emision_co2_kg"])
        excede = emision_mes > cfg.meta_mensual_co2_kg
        return {
            "desde": desde, "hasta": hasta, "hay_datos": hay_datos,
            "mensaje": None if hay_datos else "No hay datos suficientes: ejecute al menos una jornada operativa antes de generar el plan.",
            "emision_co2_kg": emision, "toneladas_co2": emision / 1000.0, "kg_co2_por_arbol_anio": cfg.kg_co2_por_arbol_anio,
            "arboles_necesarios": math.ceil(emision / cfg.kg_co2_por_arbol_anio) if hay_datos else 0,
            "mes_evaluado": {
                "desde": inicio_mes, "hasta": hasta, "emision_co2_kg": emision_mes, "meta_kg": cfg.meta_mensual_co2_kg,
                "porcentaje_meta": 100.0 * emision_mes / cfg.meta_mensual_co2_kg, "excede_meta": excede,
            },
            "acciones": ACCIONES_DE_REDUCCION if excede else [],
            "alianzas": ALIANZAS_DE_REFORESTACION if hay_datos else [],
        }
