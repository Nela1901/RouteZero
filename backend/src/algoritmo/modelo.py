"""Tipos de datos del motor de rutas.

Este paquete no depende de FastAPI, SQLAlchemy ni de ningún otro módulo del backend: recibe un
`Problema` con datos simples (matrices y listas) y devuelve un `Resultado`. Así se puede probar sin base
de datos y, más adelante, comparar con otro algoritmo (GA) sobre los mismos datos.

Convenciones: los instantes son segundos desde la medianoche; las distancias, metros; el índice 0 de las
matrices es el depósito y el pedido `i` de la lista ocupa el índice `i + 1`.
"""

from dataclasses import dataclass, field
from datetime import date

import numpy as np

PRIORIDADES = ("EXPRESS", "ESTANDAR", "ECONOMICO")

# Motivos por los que un pedido puede quedar sin cobertura
PESO_EXCEDE_CAPACIDAD = "PESO_EXCEDE_CAPACIDAD"
SIN_RECURSOS = "SIN_RECURSOS"
FUERA_DE_JORNADA = "FUERA_DE_JORNADA"
FLOTA_INSUFICIENTE = "FLOTA_INSUFICIENTE"


@dataclass(frozen=True)
class Pedido:
    id: str
    peso_kg: float
    prioridad: str
    ventana_inicio_s: int
    ventana_fin_s: int


@dataclass(frozen=True)
class Vehiculo:
    id: str
    placa: str
    tipo: str  # CAMIONETA | FURGON | MOTO
    capacidad_kg: float
    consumo_km_l: float
    factor_co2_kg_km: float
    estado: str = "DISPONIBLE"


@dataclass(frozen=True)
class Conductor:
    id: str
    categoria_licencia: str
    licencia_vence: date
    inicio_s: int  # inicio de su disponibilidad horaria
    fin_s: int
    disponible: bool = True


@dataclass(frozen=True)
class Par:
    """Un vehículo con el conductor que lo manejará esa jornada."""

    vehiculo: Vehiculo
    conductor: Conductor


@dataclass
class Parametros:
    fecha: date
    hora_inicio_jornada_s: int = 8 * 3600
    atencion_s: int = 600                 # tiempo fijo de atención por parada
    jornada_max_s: int = 8 * 3600         # RN-002
    descanso_cada_s: int = 4 * 3600       # RN-003: tras 4 h de trabajo continuo...
    descanso_s: int = 3600                # ...un descanso de 1 h
    # Función objetivo: km, litros, kg de CO2 y minutos de retraso ponderados por prioridad
    peso_distancia: float = 1.0
    peso_combustible: float = 1.0
    peso_co2: float = 2.0
    peso_retraso: float = 0.5
    ponderacion_prioridad: dict = field(default_factory=lambda: {"EXPRESS": 5.0, "ESTANDAR": 1.0, "ECONOMICO": 0.5})
    penalizacion_sin_cobertura: float = 1000.0
    # Restricción de circulación (RN-004): último dígito de placa -> días de la semana restringidos (0 = lunes)
    restriccion_placa: dict | None = None
    # Búsqueda ACO
    tiempo_max_s: float | None = 30.0     # None: sin límite de tiempo (solo iteraciones, reproducible)
    max_iteraciones: int = 500
    iteraciones_sin_mejora: int = 50
    hormigas: int = 20
    alfa: float = 1.0
    beta: float = 3.0
    rho: float = 0.1
    q0: float = 0.9
    semilla: int | None = None
    reserva_mejora_local: float = 0.15    # fracción del tiempo que se deja para pulir la mejor solución


@dataclass
class Problema:
    pedidos: list
    vehiculos: list
    conductores: list
    distancia_m: np.ndarray
    tiempo_s: np.ndarray
    parametros: Parametros


@dataclass
class Parada:
    pedido_id: str
    orden: int
    llegada_s: float
    inicio_atencion_s: float
    retraso_s: float


@dataclass
class Itinerario:
    """Resultado de simular una ruta: tiempos, métricas y validez."""

    salida_s: float
    regreso_s: float
    distancia_m: float
    litros: float
    co2_kg: float
    retraso_ponderado_min: float
    costo: float
    descansos: int
    paradas: list
    valida: bool
    motivo_invalida: str = ""

    @property
    def duracion_s(self) -> float:
        return self.regreso_s - self.salida_s


@dataclass
class RutaResultado:
    par: Par
    itinerario: Itinerario


@dataclass
class SinCobertura:
    pedido_id: str
    motivo: str
    sugerencia: str


@dataclass
class Resultado:
    rutas: list
    sin_cobertura: list
    costo: float
    costo_base: float
    distancia_base_m: float
    distancia_m: float
    co2_base_kg: float
    co2_kg: float
    litros_base: float
    litros: float
    iteraciones: int
    tiempo_s: float
    imposible: bool = False
    mensaje: str = ""

    @property
    def mejora_distancia_pct(self) -> float:
        return 100.0 * (self.distancia_base_m - self.distancia_m) / self.distancia_base_m if self.distancia_base_m else 0.0

    @property
    def mejora_co2_pct(self) -> float:
        return 100.0 * (self.co2_base_kg - self.co2_kg) / self.co2_base_kg if self.co2_base_kg else 0.0
