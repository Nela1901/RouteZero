"""Punto de entrada del motor: `resolver(problema)` devuelve rutas válidas o explica por qué no hay."""

import time

import numpy as np

from src.algoritmo.aco import optimizar
from src.algoritmo.busqueda_local import mejorar
from src.algoritmo.cobertura import SUGERENCIAS, sin_cobertura
from src.algoritmo.construccion import solucion_voraz
from src.algoritmo.emparejamiento import emparejar
from src.algoritmo.evaluacion import ContextoPar, Datos
from src.algoritmo.modelo import SIN_RECURSOS, Problema, Resultado, RutaResultado, SinCobertura

EVALUACIONES_PULIDO_FINAL_FIJO = 3000     # sin límite de tiempo: resultado reproducible
EVALUACIONES_PULIDO_FINAL_POR_TIEMPO = 50_000


def _totales(itinerarios: list) -> tuple:
    return (
        sum(i.distancia_m for i in itinerarios),
        sum(i.co2_kg for i in itinerarios),
        sum(i.litros for i in itinerarios),
    )


def resolver(problema: Problema) -> Resultado:
    inicio = time.perf_counter()
    p = problema.parametros
    d = Datos(problema)

    if d.n == 0:
        return Resultado([], [], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, mensaje="No hay pedidos pendientes.")

    emparejamiento = emparejar(problema.vehiculos, problema.conductores, p)
    if not emparejamiento.pares:
        sin = [SinCobertura(x.id, SIN_RECURSOS, SUGERENCIAS[SIN_RECURSOS]) for x in problema.pedidos]
        return Resultado(
            [], sin, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, time.perf_counter() - inicio,
            imposible=True,
            mensaje=(
                "No es posible generar rutas: no hay vehículos disponibles y conductores elegibles "
                f"({emparejamiento.vehiculos_elegibles} vehículos y {emparejamiento.conductores_elegibles} conductores "
                "elegibles, sin pareja compatible)."
            ),
        )

    contextos = [ContextoPar.crear(par, p) for par in emparejamiento.pares]
    base = solucion_voraz(d, contextos)
    rng = np.random.default_rng(p.semilla)

    mejor, iteraciones = optimizar(d, contextos, base, rng, inicio)
    limite_final = None if p.tiempo_max_s is None else inicio + p.tiempo_max_s
    evaluaciones = EVALUACIONES_PULIDO_FINAL_FIJO if p.tiempo_max_s is None else EVALUACIONES_PULIDO_FINAL_POR_TIEMPO
    mejor = mejorar(mejor, d, contextos, rng, limite_final, evaluaciones)
    if mejor.costo > base.costo:  # la solución devuelta nunca es peor que la inicial
        mejor = base

    distancia, co2, litros = _totales(mejor.itinerarios)
    distancia_b, co2_b, litros_b = _totales(base.itinerarios)
    rutas = [RutaResultado(emparejamiento.pares[k], itin) for (k, _), itin in zip(mejor.rutas, mejor.itinerarios)]
    return Resultado(
        rutas=rutas,
        sin_cobertura=sin_cobertura(mejor.sin_asignar, contextos, d),
        costo=mejor.costo,
        costo_base=base.costo,
        distancia_base_m=distancia_b,
        distancia_m=distancia,
        co2_base_kg=co2_b,
        co2_kg=co2,
        litros_base=litros_b,
        litros=litros,
        iteraciones=iteraciones,
        tiempo_s=time.perf_counter() - inicio,
    )
