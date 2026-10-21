"""Punto de entrada del motor: `resolver(problema)` devuelve rutas válidas o explica por qué no hay."""

import time

import numpy as np

from src.algoritmo.aco import optimizar
from src.algoritmo.busqueda_local import mejorar
from src.algoritmo.cobertura import SUGERENCIAS, sin_cobertura
from src.algoritmo.construccion import evaluar_solucion, solucion_voraz
from src.algoritmo.emparejamiento import Emparejamiento, emparejar
from src.algoritmo.evaluacion import ContextoPar, Datos
from src.algoritmo.modelo import SIN_RECURSOS, Problema, Resultado, RutaResultado, SinCobertura

EVALUACIONES_PULIDO_FINAL_FIJO = 3000     # sin límite de tiempo: resultado reproducible
EVALUACIONES_PULIDO_FINAL_POR_TIEMPO = 50_000
EVALUACIONES_INSERCION_PLAN_VIGENTE = 300  # al insertar los pedidos nuevos en el plan que ya existe


def _totales(itinerarios: list) -> tuple:
    return (
        sum(i.distancia_m for i in itinerarios),
        sum(i.co2_kg for i in itinerarios),
        sum(i.litros for i in itinerarios),
    )


def _solucion_desde_plan(problema: Problema, d: Datos, contextos: list, pares: list, rng):
    """Punto de partida de una re-optimización: el plan vigente (sin las paradas que ya no existen) con los
    pedidos nuevos insertados donde menos cuestan. Una ruta que deje de ser válida (p. ej. por un incidente
    de tráfico) se descarta y sus pedidos vuelven a repartirse."""
    indice = {x.id: i for i, x in enumerate(problema.pedidos)}
    rutas, usados = [], set()
    for k, par in enumerate(pares):
        secuencia = [indice[i] for i in problema.plan_vigente.get(par.vehiculo.id, []) if i in indice]
        if secuencia:
            rutas.append((k, secuencia))
            usados.update(secuencia)
    sin = [i for i in range(d.n) if i not in usados]
    inicial = evaluar_solucion(d, contextos, rutas, sin)
    return mejorar(inicial, d, contextos, rng, None, EVALUACIONES_INSERCION_PLAN_VIGENTE)


def resolver(problema: Problema) -> Resultado:
    inicio = time.perf_counter()
    p = problema.parametros
    d = Datos(problema)

    if d.n == 0:
        return Resultado([], [], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, mensaje="No hay pedidos pendientes.")

    if problema.pares_fijos is not None:
        emparejamiento = Emparejamiento(list(problema.pares_fijos), len(problema.pares_fijos), len(problema.pares_fijos))
    else:
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

    contextos = [ContextoPar.crear(par, p, problema.arranques.get(par.vehiculo.id)) for par in emparejamiento.pares]
    rng = np.random.default_rng(p.semilla)
    base = solucion_voraz(d, contextos)
    if problema.plan_vigente:  # re-optimización: se parte del plan que ya existe si no es peor que la solución voraz
        vigente = _solucion_desde_plan(problema, d, contextos, emparejamiento.pares, rng)
        if vigente.costo <= base.costo:
            base = vigente

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
