"""Generadores de problemas sintéticos para probar el motor sin base de datos."""

from datetime import date, timedelta

import numpy as np

from src.algoritmo.modelo import Conductor, Parametros, Pedido, Problema, Vehiculo

FECHA = date(2026, 10, 12)  # lunes
METROS_POR_SEGUNDO = 25 / 3.6


def hora(h: float) -> int:
    return int(h * 3600)


def matrices_planas(coords_km: np.ndarray, sinuosidad: float = 1.3):
    """Matrices (depósito en la fila 0) con distancia euclidiana × sinuosidad y velocidad de 25 km/h."""
    diff = coords_km[:, None, :] - coords_km[None, :, :]
    distancia = np.sqrt((diff**2).sum(axis=2)) * 1000.0 * sinuosidad
    return distancia, distancia / METROS_POR_SEGUNDO


def problema_aleatorio(
    n_pedidos: int = 30,
    n_vehiculos: int = 4,
    semilla: int = 1,
    peso_max: float = 120.0,
    capacidad: tuple = (600.0, 1500.0),
    pct_express: float = 0.1,
    **parametros,
) -> Problema:
    azar = np.random.default_rng(semilla)
    coords = azar.uniform(0, 8, size=(n_pedidos + 1, 2))
    coords[0] = (4.0, 4.0)  # depósito al centro
    distancia, tiempo = matrices_planas(coords)

    pedidos = []
    for i in range(n_pedidos):
        inicio = float(azar.uniform(8, 11.5))
        pedidos.append(
            Pedido(
                id=f"P{i:03d}",
                peso_kg=float(azar.uniform(5, peso_max)),
                prioridad="EXPRESS" if azar.random() < pct_express else str(azar.choice(["ESTANDAR", "ECONOMICO"])),
                ventana_inicio_s=hora(inicio),
                ventana_fin_s=hora(inicio + float(azar.uniform(2, 4))),
            )
        )
    vehiculos = [
        Vehiculo(
            id=f"V{i:02d}",
            placa=f"ABC-{100 + i}",
            tipo="CAMIONETA" if i % 2 == 0 else "FURGON",
            capacidad_kg=float(azar.uniform(*capacidad)),
            consumo_km_l=float(azar.uniform(8, 12)),
            factor_co2_kg_km=float(azar.uniform(0.18, 0.32)),
        )
        for i in range(n_vehiculos)
    ]
    conductores = [
        Conductor(f"C{i:02d}", "A-IIb", FECHA + timedelta(days=365), hora(6), hora(14)) for i in range(n_vehiculos)
    ]
    parametros.setdefault("semilla", semilla)
    return Problema(pedidos, vehiculos, conductores, distancia, tiempo, Parametros(fecha=FECHA, **parametros))
