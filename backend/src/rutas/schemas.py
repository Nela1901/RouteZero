from datetime import date, time
from decimal import Decimal

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


class ResultadoConfirmacion(BaseModel):
    lote_id: str
    rutas_confirmadas: int
    pedidos_asignados: int


class ResultadoDescarte(BaseModel):
    lote_id: str
    rutas_eliminadas: int
