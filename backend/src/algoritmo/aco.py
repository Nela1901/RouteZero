"""Optimización por colonia de hormigas (ACO, variante tipo ACS) sobre la solución inicial voraz.

Cada iteración, un grupo de hormigas construye soluciones guiadas por una matriz de feromonas y por la
visibilidad (inverso del costo incremental y de la holgura de la ventana). La mejor solución encontrada
refuerza sus arcos (evaporación `rho` y depósito `rho / costo`) y, cuando mejora, se pule con búsqueda
local. La búsqueda termina por tiempo, por iteraciones sin mejora o por un máximo de iteraciones.
"""

import time

import numpy as np

from src.algoritmo.busqueda_local import mejorar
from src.algoritmo.construccion import Solucion, construir, evaluar_solucion
from src.algoritmo.evaluacion import Datos

TOLERANCIA = 1e-9
EVALUACIONES_PULIDO_CORTO = 300


def _reforzar(tau: np.ndarray, mejor: Solucion, rho: float) -> None:
    deposito = rho / max(mejor.costo, 1e-9)
    for i, j in mejor.arcos():
        tau[i, j] = (1.0 - rho) * tau[i, j] + deposito


def optimizar(d: Datos, contextos: list, inicial: Solucion, rng, inicio_t: float) -> tuple:
    """Devuelve (mejor solución, iteraciones realizadas)."""
    p = d.p
    hormigas = min(p.hormigas, max(2, d.n))
    tau0 = 1.0 / (max(d.n, 1) * max(inicial.costo, 1e-6))
    tau = np.full((d.n + 1, d.n + 1), tau0)
    limite = None if p.tiempo_max_s is None else inicio_t + p.tiempo_max_s * (1.0 - p.reserva_mejora_local)

    def sin_tiempo() -> bool:
        return limite is not None and time.perf_counter() >= limite

    mejor = inicial
    _reforzar(tau, mejor, p.rho)
    sin_mejora = 0
    iteracion = 0
    for iteracion in range(1, p.max_iteraciones + 1):
        if sin_tiempo():
            iteracion -= 1
            break
        mejor_iteracion = None
        for _ in range(hormigas):
            rutas, sin = construir(d, contextos, tau, rng, p.q0, p.alfa, p.beta)
            solucion = evaluar_solucion(d, contextos, rutas, sin)
            if mejor_iteracion is None or solucion.costo < mejor_iteracion.costo:
                mejor_iteracion = solucion
            if sin_tiempo():
                break
        if mejor_iteracion is not None and mejor_iteracion.costo < mejor.costo - TOLERANCIA:
            mejor = mejorar(mejor_iteracion, d, contextos, rng, limite, EVALUACIONES_PULIDO_CORTO)
            sin_mejora = 0
        else:
            sin_mejora += 1
        _reforzar(tau, mejor, p.rho)
        if sin_mejora >= p.iteraciones_sin_mejora:
            break
    return mejor, iteracion
