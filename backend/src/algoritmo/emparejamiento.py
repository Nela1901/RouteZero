"""Elegibilidad y emparejamiento de vehículos y conductores para una jornada.

Reglas (spec `route-optimization`):
- solo vehículos en estado DISPONIBLE y sin restricción de circulación vigente ese día (RN-004);
- solo conductores disponibles con la licencia vigente en la fecha de la jornada;
- cada vehículo se empareja con un conductor cuya categoría de licencia sea compatible con su tipo.

Compatibilidad (supuesto del diseño, ajustable): las categorías `A-*` conducen CAMIONETA y FURGON; las
`B-IIa` y `B-IIb`, MOTO.
"""

from dataclasses import dataclass, field

from src.algoritmo.modelo import Conductor, Par, Parametros, Vehiculo

CATEGORIAS_MOTO = ("B-IIa", "B-IIb")


def licencia_compatible(tipo_vehiculo: str, categoria: str) -> bool:
    if tipo_vehiculo in ("CAMIONETA", "FURGON"):
        return categoria.startswith("A-")
    if tipo_vehiculo == "MOTO":
        return categoria in CATEGORIAS_MOTO
    return False


def ultimo_digito(placa: str) -> int | None:
    for caracter in reversed(placa):
        if caracter.isdigit():
            return int(caracter)
    return None


def vehiculo_restringido(vehiculo: Vehiculo, p: Parametros) -> bool:
    """RN-004: ¿tiene el vehículo restricción de circulación en la fecha? Sin tabla configurada, nunca."""
    if not p.restriccion_placa:
        return False
    digito = ultimo_digito(vehiculo.placa)
    return digito is not None and p.fecha.weekday() in p.restriccion_placa.get(digito, ())


@dataclass
class Emparejamiento:
    pares: list
    vehiculos_elegibles: int = 0
    conductores_elegibles: int = 0
    vehiculos_restringidos: list = field(default_factory=list)


def _costo_por_km(v: Vehiculo, p: Parametros) -> float:
    return p.peso_distancia + p.peso_combustible / v.consumo_km_l + p.peso_co2 * v.factor_co2_kg_km


def emparejar(vehiculos: list, conductores: list, p: Parametros) -> Emparejamiento:
    """Forma los pares vehículo-conductor ordenados del más eficiente al menos eficiente.

    Como cada categoría de conductor solo puede manejar una familia de vehículos (A-* con camionetas y
    furgones, B-II* con motos), el emparejamiento voraz forma el máximo de pares posible: dentro de cada
    familia, el vehículo de mayor capacidad recibe al conductor con la disponibilidad más amplia.
    """
    restringidos = [v.placa for v in vehiculos if v.estado == "DISPONIBLE" and vehiculo_restringido(v, p)]
    elegibles_v = [v for v in vehiculos if v.estado == "DISPONIBLE" and not vehiculo_restringido(v, p)]
    elegibles_c = [c for c in conductores if c.disponible and c.licencia_vence > p.fecha]

    pares: list[Par] = []
    libres: list[Conductor] = sorted(elegibles_c, key=lambda c: (-(c.fin_s - c.inicio_s), c.id))
    for v in sorted(elegibles_v, key=lambda v: (-v.capacidad_kg, v.id)):
        for c in libres:
            if licencia_compatible(v.tipo, c.categoria_licencia):
                pares.append(Par(v, c))
                libres.remove(c)
                break

    pares.sort(key=lambda par: (_costo_por_km(par.vehiculo, p), -par.vehiculo.capacidad_kg, par.vehiculo.id))
    return Emparejamiento(pares, len(elegibles_v), len(elegibles_c), restringidos)
