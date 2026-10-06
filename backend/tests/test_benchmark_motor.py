"""Benchmark del motor (RN-015, RNF-001): 150 pedidos y 15 vehículos sobre el grafo real de Huancayo.

Se ejecuta aparte de la suite normal:  pytest tests/test_benchmark_motor.py -m benchmark -s --no-cov

- `test_percentil_95_del_tiempo_total`: 10 ejecuciones completas (matrices por calles + optimización con el
  presupuesto de tiempo por defecto) y comprobación de que el percentil 95 no supera 45 s.
- `test_sensibilidad_del_tiempo_de_atencion`: el mismo escenario con 5, 10 y 15 minutos de atención por
  parada, para registrar cuánto cambia el resultado (el valor de diseño es 10).
"""

import random
import time
from datetime import timedelta

import numpy as np
import pytest
from ayudas_algoritmo import FECHA, hora

from src.algoritmo.modelo import Conductor, Parametros, Pedido, Problema, Vehiculo
from src.algoritmo.motor import resolver
from src.red_vial.grafo import RUTA_POR_DEFECTO
from src.red_vial.matrices import RedVial

DEPOSITO = (-12.043632, -75.226373)
LIMITE_S = 45.0

pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.skipif(not RUTA_POR_DEFECTO.exists(), reason="No existe data/huancayo_grafo.npz"),
]


def escenario(semilla: int, n_pedidos: int = 150, n_vehiculos: int = 15, **parametros) -> tuple:
    """Devuelve (problema, segundos que tardó calcular las matrices por calles)."""
    azar = random.Random(semilla)
    puntos = [DEPOSITO] + [(azar.uniform(-12.10, -12.00), azar.uniform(-75.26, -75.18)) for _ in range(n_pedidos)]
    inicio = time.perf_counter()
    m = RedVial.cargar(0.6).matrices(puntos)
    t_matrices = time.perf_counter() - inicio

    pedidos = []
    for i in range(n_pedidos):
        abre = azar.uniform(8, 12)
        pedidos.append(
            Pedido(
                f"P{i:03d}",
                azar.uniform(10, 200),
                "EXPRESS" if azar.random() < 0.1 else azar.choice(["ESTANDAR", "ESTANDAR", "ECONOMICO"]),
                hora(abre),
                hora(abre + azar.uniform(2, 4)),
            )
        )
    vehiculos = [
        Vehiculo(
            f"V{i:02d}", f"ABC-{100 + i}", "CAMIONETA" if i % 3 else "FURGON",
            azar.uniform(500, 3000), azar.uniform(8, 12), azar.uniform(0.15, 0.35),
        )
        for i in range(n_vehiculos)
    ]
    conductores = [Conductor(f"C{i:02d}", "A-IIb", FECHA + timedelta(days=200), hora(6), hora(14)) for i in range(n_vehiculos)]
    parametros.setdefault("semilla", semilla)
    problema = Problema(pedidos, vehiculos, conductores, m.distancia_m, m.tiempo_s, Parametros(fecha=FECHA, **parametros))
    return problema, t_matrices


def resumen(r) -> dict:
    paradas = [p for x in r.rutas for p in x.itinerario.paradas]
    return {
        "rutas": len(r.rutas),
        "atendidos": len(paradas),
        "sin_cobertura": len(r.sin_cobertura),
        "tardias": sum(1 for p in paradas if p.retraso_s > 0),
        "km": r.distancia_m / 1000,
        "co2": r.co2_kg,
        "litros": r.litros,
        "costo": r.costo,
        "mejora_costo_pct": 100 * (r.costo_base - r.costo) / r.costo_base if r.costo_base else 0.0,
    }


def test_percentil_95_del_tiempo_total():
    totales, filas = [], []
    for semilla in range(1, 11):
        problema, t_matrices = escenario(semilla)
        r = resolver(problema)
        total = t_matrices + r.tiempo_s
        totales.append(total)
        assert all(x.itinerario.valida for x in r.rutas)
        fila = resumen(r)
        filas.append(fila)
        print(
            f"  corrida {semilla:2d}: total {total:5.1f} s (matrices {t_matrices:.2f} s, motor {r.tiempo_s:5.1f} s, "
            f"{r.iteraciones} iteraciones) | rutas {fila['rutas']}, atendidos {fila['atendidos']}/150, "
            f"sin cobertura {fila['sin_cobertura']}, mejora de costo {fila['mejora_costo_pct']:.0f} %"
        )
    p95 = float(np.percentile(totales, 95))
    print(f"\n  Percentil 95 del tiempo total: {p95:.1f} s (límite {LIMITE_S:.0f} s); máximo {max(totales):.1f} s; mediana {np.median(totales):.1f} s")
    assert p95 <= LIMITE_S


def test_sensibilidad_del_tiempo_de_atencion():
    print("\n  atención | rutas | atendidos | sin cobertura | entregas tardías |    km |  CO2 kg | costo")
    resultados = {}
    for minutos in (5, 10, 15):
        problema, _ = escenario(3, atencion_s=minutos * 60, tiempo_max_s=10.0)
        r = resolver(problema)
        assert all(x.itinerario.valida for x in r.rutas)
        f = resumen(r)
        resultados[minutos] = f
        print(
            f"   {minutos:4d} min | {f['rutas']:5d} | {f['atendidos']:9d} | {f['sin_cobertura']:13d} | "
            f"{f['tardias']:16d} | {f['km']:5.1f} | {f['co2']:7.1f} | {f['costo']:7.0f}"
        )
    # A más tiempo de atención por parada, caben menos paradas por jornada: nunca se atienden más pedidos
    assert resultados[15]["atendidos"] <= resultados[5]["atendidos"]
