from datetime import date, datetime, time
from decimal import Decimal

from typing import Literal

from pydantic import BaseModel, Field


class GenerarRutas(BaseModel):
    fecha_jornada: date
    # Presupuesto total de la generación en segundos (por defecto 30; el servidor lo limita a 40)
    tiempo_max_s: float | None = Field(default=None, gt=0)


class VehiculoRuta(BaseModel):
    vehiculo_id: str
    placa: str
    tipo: str


class ConductorRuta(BaseModel):
    conductor_id: str
    nombre: str


class MetricasRuta(BaseModel):
    emision_co2_kg: Decimal
    combustible_l: Decimal
    combustible_ahorrado_l: Decimal
    distancia_km: Decimal
    cumplimiento_ventanas_pct: Decimal


class ParadaOut(BaseModel):
    orden: int
    pedido_id: str
    cliente: str
    descripcion: str | None
    peso_kg: Decimal
    prioridad: str
    latitud: Decimal
    longitud: Decimal
    hora_estimada: time | None
    minutos_retraso: int
    estado_entrega: str = "PENDIENTE"  # PENDIENTE | ENTREGADO | FALLIDO
    pedido_estado: str = "ASIGNADO"    # un pedido CANCELADO sigue en la ruta hasta que se re-optimice


class RutaOut(BaseModel):
    ruta_id: str
    lote_id: str
    fecha_jornada: date
    estado: str
    vehiculo: VehiculoRuta
    conductor: ConductorRuta
    hora_salida: time | None
    hora_regreso: time | None
    distancia_km: Decimal | None
    tiempo_min: int | None
    cantidad_paradas: int
    metricas: MetricasRuta | None
    paradas: list[ParadaOut] = []
    # Solo en el borrador de una re-optimización: ruta en curso a la que reemplazará al confirmarse
    reemplaza_ruta_id: str | None = None


class SinCoberturaOut(BaseModel):
    pedido_id: str
    motivo: str
    sugerencia: str


class ComparativaBase(BaseModel):
    """Mejora del motor respecto de la solución voraz inicial."""

    costo_base: float
    costo: float
    distancia_base_km: float
    distancia_km: float
    mejora_distancia_pct: float
    co2_base_kg: float
    co2_kg: float
    mejora_co2_pct: float


class ResultadoGeneracion(BaseModel):
    lote_id: str | None
    fecha_jornada: date
    imposible: bool
    mensaje: str
    rutas: list[RutaOut]
    sin_cobertura: list[SinCoberturaOut]
    fuente_distancias: str  # "calles" | "mixta" | "aproximada"
    puntos_aproximados: int
    comparativa_base: ComparativaBase | None
    iteraciones: int
    tiempo_ejecucion_s: float
    # Diagnóstico: segundos por fase y pico de memoria del proceso (solo en Linux)
    tiempos: dict[str, float] = {}
    memoria_pico_mb: float | None = None


class ResultadoConfirmacion(BaseModel):
    lote_id: str
    rutas_confirmadas: int
    pedidos_asignados: int


class ResultadoDescarte(BaseModel):
    lote_id: str
    rutas_eliminadas: int


# ---------------------------------------------------------------------------------- HU-012: re-optimización
CalleIncidente = Literal["Av. Ferrocarril", "Av. Giráldez", "Calle Real"]  # RN-012


class Reoptimizar(BaseModel):
    fecha_jornada: date
    # Presupuesto total en segundos; el servidor lo limita a 30 (RN-012)
    tiempo_max_s: float | None = Field(default=None, gt=0)
    # Solo para pruebas y demostraciones: hora que se toma como "ahora" (HH:MM). Sin ella se usa la hora real de Perú.
    hora_actual: time | None = None


class ComparativaReoptimizacion(BaseModel):
    """Plan vigente (con los pedidos nuevos insertados) frente al plan re-optimizado, sobre el tramo que falta."""

    costo_base: float
    costo: float
    distancia_base_km: float
    distancia_km: float


class ResultadoReoptimizacion(BaseModel):
    lote_id: str | None
    fecha_jornada: date
    sin_rutas_activas: bool
    mensaje: str
    hora_considerada: time | None
    rutas: list[RutaOut]
    sin_cobertura: list[SinCoberturaOut]
    pedidos_nuevos: int       # pendientes que se integraron al plan
    pedidos_retirados: int    # paradas pendientes cuyo pedido se canceló
    incidentes_aplicados: list[str]
    comparativa: ComparativaReoptimizacion | None
    fuente_distancias: str
    iteraciones: int
    tiempo_ejecucion_s: float
    dentro_del_limite: bool   # tiempo_ejecucion_s <= 30 (RN-012)
    tiempos: dict[str, float] = {}


class IncidenteIn(BaseModel):
    calle: CalleIncidente
    factor: float = Field(default=2.0, gt=1.0, le=10.0)  # 2.0 = el doble de lento
    descripcion: str | None = Field(default=None, max_length=200)


class IncidenteOut(BaseModel):
    incidente_id: str
    calle: str
    factor: float
    descripcion: str | None
    activo: bool
    creado_en: datetime
    resuelto_en: datetime | None


class MarcarEntrega(BaseModel):
    estado: Literal["ENTREGADO", "FALLIDO"]


class ResultadoEntrega(BaseModel):
    ruta_id: str
    pedido_id: str
    estado_entrega: str
    estado_ruta: str  # EN_EJECUCION | COMPLETADA


# ---------------------------------------------------------------------------------- HU-013: mapa
class DepositoOut(BaseModel):
    latitud: float
    longitud: float


class TramoMapa(BaseModel):
    desde: int  # orden de la parada de origen (0 = depósito)
    hasta: int  # orden de la parada de destino (0 = regreso al depósito)
    distancia_km: float
    duracion_min: float
    en_punta: bool  # el tramo sale en una franja de hora punta
    puntos: list[list[float]]  # [lat, lon]


class ParadaMapa(BaseModel):
    orden: int
    pedido_id: str
    cliente: str
    prioridad: str
    latitud: Decimal
    longitud: Decimal
    hora_estimada: time | None
    minutos_retraso: int
    estado_entrega: str = "PENDIENTE"
    pedido_estado: str = "ASIGNADO"


class RutaMapa(BaseModel):
    ruta_id: str
    lote_id: str
    estado: str
    reemplaza_ruta_id: str | None = None
    vehiculo: VehiculoRuta
    conductor: ConductorRuta
    hora_salida: time | None
    hora_regreso: time | None
    paradas: list[ParadaMapa]
    tramos: list[TramoMapa]


class MapaOut(BaseModel):
    fecha_jornada: date
    deposito: DepositoOut
    rutas: list[RutaMapa]


class ViaCongestion(BaseModel):
    calle: str
    nivel: Literal["VERDE", "AMARILLO", "ROJO"]
    factor: float  # cuántas veces más lenta que de costumbre
    motivos: list[str]  # "hora punta", "incidente"
    segmentos: list[list[list[float]]]  # cada segmento: dos puntos [lat, lon]


class CongestionOut(BaseModel):
    hora: time
    en_punta: bool
    vias: list[ViaCongestion]
