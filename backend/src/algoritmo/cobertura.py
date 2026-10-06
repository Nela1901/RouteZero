"""Pedidos sin cobertura: motivo y acción sugerida (HU-011, escenario "sin vehículos o capacidad insuficiente")."""

from src.algoritmo.evaluacion import ContextoPar, Datos, simular_ruta
from src.algoritmo.modelo import (
    FLOTA_INSUFICIENTE,
    FUERA_DE_JORNADA,
    PESO_EXCEDE_CAPACIDAD,
    SIN_RECURSOS,
    SinCobertura,
)

SUGERENCIAS = {
    SIN_RECURSOS: "Revise que haya vehículos DISPONIBLES y conductores disponibles con licencia vigente y compatible con el tipo de vehículo.",
    PESO_EXCEDE_CAPACIDAD: "Divida el pedido en envíos más livianos o incorpore un vehículo de mayor capacidad.",
    FUERA_DE_JORNADA: "El pedido no se puede atender dentro de la jornada de ningún conductor: revise su ubicación y amplíe el horario de algún conductor.",
    FLOTA_INSUFICIENTE: "La flota disponible no alcanza para todos los pedidos de la jornada: incorpore más vehículos o conductores, o reprograme los pedidos menos urgentes.",
}


def motivo_de(c: int, contextos: list, d: Datos) -> str:
    """Por qué el pedido `c` (índice) no pudo asignarse."""
    if not contextos:
        return SIN_RECURSOS
    if d.peso_l[c] > max(ctx.capacidad_kg for ctx in contextos):
        return PESO_EXCEDE_CAPACIDAD
    if not any(simular_ruta([c], ctx, d).valida for ctx in contextos):
        return FUERA_DE_JORNADA
    return FLOTA_INSUFICIENTE


def sin_cobertura(indices: list, contextos: list[ContextoPar], d: Datos) -> list:
    resultado = []
    for c in indices:
        motivo = motivo_de(c, contextos, d)
        resultado.append(SinCobertura(d.pedidos[c].id, motivo, SUGERENCIAS[motivo]))
    return resultado
