from datetime import date

from pydantic import BaseModel


class Totales(BaseModel):
    rutas: int
    distancia_km: float
    emision_co2_kg: float
    combustible_l: float
    combustible_ahorrado_l: float
    ahorro_soles: float
    cumplimiento_ventanas_pct: float


class Entregas(BaseModel):
    entregadas: int
    pendientes: int
    fallidas: int


class DiaSostenibilidad(BaseModel):
    fecha: date
    emision_co2_kg: float
    distancia_km: float
    combustible_ahorrado_l: float


class DashboardOut(BaseModel):
    desde: date
    hasta: date
    hay_datos: bool
    mensaje: str | None
    totales: Totales
    entregas: Entregas
    por_dia: list[DiaSostenibilidad]
    precio_combustible_soles_l: float


class MesEvaluado(BaseModel):
    desde: date
    hasta: date
    emision_co2_kg: float
    meta_kg: float
    porcentaje_meta: float
    excede_meta: bool


class Alianza(BaseModel):
    nombre: str
    descripcion: str


class CompensacionOut(BaseModel):
    desde: date
    hasta: date
    hay_datos: bool
    mensaje: str | None
    emision_co2_kg: float
    toneladas_co2: float
    kg_co2_por_arbol_anio: float
    arboles_necesarios: int
    mes_evaluado: MesEvaluado
    acciones: list[str]
    alianzas: list[Alianza]
