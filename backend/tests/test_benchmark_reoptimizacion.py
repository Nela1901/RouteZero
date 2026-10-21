"""Benchmark de la re-optimización (RN-012, HU-012): 150 pedidos y 15 vehículos sobre el grafo real de Huancayo,
con las rutas ya en curso, pedidos nuevos y congestión en Av. Ferrocarril y Av. Giráldez.

Se ejecuta aparte de la suite normal:  pytest tests/test_benchmark_reoptimizacion.py -m benchmark -s --no-cov

Mide en esta máquina; el límite de 30 s hay que comprobarlo también en Render (CPU limitada) con los campos
`tiempos` y `tiempo_ejecucion_s` de la respuesta de `POST /api/rutas/reoptimizar`.
"""

import random
import time

import numpy as np
import pytest
from ayudas_algoritmo import hora
from test_benchmark_motor import DEPOSITO, escenario

from src.algoritmo.modelo import Arranque, Par, Pedido, Problema
from src.algoritmo.motor import resolver
from src.red_vial.grafo import RUTA_POR_DEFECTO
from src.red_vial.matrices import RedVial
from src.rutas import congestion

LIMITE_S = 30.0          # RN-012: lo que no se puede superar
PRESUPUESTO_S = 25.0     # lo que apunta el servicio, para dejar holgura
RESERVA_PERSISTENCIA_S = 5.0  # igual que el servicio: tiempo para guardar el borrador
AHORA_S = hora(10)

pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.skipif(not RUTA_POR_DEFECTO.exists(), reason="No existe data/huancayo_grafo.npz"),
]


def _puntos(semilla: int, cantidad: int) -> list:
    azar = random.Random(semilla)
    return [(azar.uniform(-12.10, -12.00), azar.uniform(-75.26, -75.18)) for _ in range(cantidad)]


@pytest.mark.parametrize("semilla", [1, 2, 3])
def test_la_reoptimizacion_cabe_en_el_limite_de_30_segundos(semilla):
    # Plan de la jornada: 150 pedidos, 15 vehículos
    problema, _ = escenario(semilla, tiempo_max_s=10.0)
    plan = resolver(problema)
    coordenadas = [DEPOSITO] + _puntos(semilla, 150)  # las mismas que usó `escenario`
    indice = {x.id: i for i, x in enumerate(problema.pedidos)}

    # A las 10:00 cada ruta ya entregó sus dos primeras paradas y llegan 10 pedidos urgentes
    entregados = {p.pedido_id for r in plan.rutas for p in r.itinerario.paradas[:2]}
    restantes = [x for x in problema.pedidos if x.id not in entregados]
    azar = random.Random(100 + semilla)
    nuevos = [
        Pedido(f"N{i:02d}", azar.uniform(5, 40), "EXPRESS", hora(10), hora(13))
        for i in range(10)
    ]
    puntos = [coordenadas[0]] + [coordenadas[indice[x.id] + 1] for x in restantes]
    puntos += _puntos(900 + semilla, len(nuevos))
    arranques, plan_vigente, pares = {}, {}, []
    for r in plan.rutas:
        hechas = r.itinerario.paradas[:2]
        arranques[r.par.vehiculo.id] = Arranque(len(puntos), float(AHORA_S), 3600.0) if hechas else Arranque(0, float(AHORA_S))
        if hechas:
            puntos.append(coordenadas[indice[hechas[-1].pedido_id] + 1])
        plan_vigente[r.par.vehiculo.id] = [p.pedido_id for p in r.itinerario.paradas[2:]]
        pares.append(r.par)

    inicio = time.perf_counter()
    incidentes = [{"calle": "Av. Ferrocarril", "factor": 3.0}, {"calle": "Av. Giráldez", "factor": 2.0}]
    normal, punta = congestion.factores_de_matrices(incidentes)
    m = RedVial.cargar(0.6).matrices(puntos, congestion=normal, congestion_punta=punta)
    t_matrices = time.perf_counter() - inicio
    parametros = problema.parametros
    parametros.tiempo_max_s = max(1.0, PRESUPUESTO_S - t_matrices - RESERVA_PERSISTENCIA_S)
    parametros.semilla = semilla
    parametros.franjas_punta = congestion.FRANJAS_PUNTA
    nuevo = Problema(
        restantes + nuevos, problema.vehiculos, problema.conductores, m.distancia_m, m.tiempo_s, parametros,
        pares_fijos=pares, arranques=arranques, plan_vigente=plan_vigente, tiempo_punta_s=m.tiempo_punta_s,
    )
    resultado = resolver(nuevo)
    total = time.perf_counter() - inicio + RESERVA_PERSISTENCIA_S

    paradas = [p.pedido_id for r in resultado.rutas for p in r.itinerario.paradas]
    sin = [s.pedido_id for s in resultado.sin_cobertura]
    print(
        f"\nsemilla {semilla}: matrices {t_matrices:.1f} s, motor {resultado.tiempo_s:.1f} s, total con reserva {total:.1f} s; "
        f"{len(nuevo.pedidos)} pedidos, {len(resultado.rutas)} rutas, {len(sin)} sin cobertura, {resultado.iteraciones} iteraciones"
    )
    assert sorted(paradas + sin) == sorted(x.id for x in nuevo.pedidos)
    assert all(r.itinerario.valida for r in resultado.rutas)
    assert total <= LIMITE_S
    assert np.isfinite(m.tiempo_s).all()
