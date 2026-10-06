"""Matrices de distancia y tiempo de viaje entre puntos, por calles reales o en línea recta."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import dijkstra

from src.red_vial.grafo import Grafo, cargar_grafo

FACTOR_RECTA = 1.35            # la distancia por calles es ~1.38 veces la recta (medido en Huancayo)
VELOCIDAD_APROX_KMH = 40.0     # calles y jirones, DS 033-2001-MTC art. 162
VELOCIDAD_ACCESO_KMH = 20.0    # tramo entre el punto y la calle más cercana
UMBRAL_SNAP_M = 500.0
BLOQUE_FUENTES = 25            # fuentes por llamada a Dijkstra: acota la memoria temporal


@dataclass
class Matrices:
    distancia_m: np.ndarray
    tiempo_s: np.ndarray
    fuente: str  # "calles" | "mixta" | "aproximada"
    puntos_aproximados: list[int] = field(default_factory=list)


def distancias_rectas(puntos) -> np.ndarray:
    """Distancia en línea recta (haversine, metros) entre todos los pares de puntos (lat, lon)."""
    p = np.radians(np.asarray(puntos, dtype=np.float64))
    lat, lon = p[:, 0][:, None], p[:, 1][:, None]
    a = np.sin((lat.T - lat) / 2) ** 2 + np.cos(lat) * np.cos(lat.T) * np.sin((lon.T - lon) / 2) ** 2
    return 2 * 6371000.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _por_bloques(matriz_dispersa, fuentes: np.ndarray) -> np.ndarray:
    """Camino más corto entre todos los pares de `fuentes`, calculado por bloques."""
    salida = np.empty((len(fuentes), len(fuentes)))
    for i in range(0, len(fuentes), BLOQUE_FUENTES):
        bloque = fuentes[i : i + BLOQUE_FUENTES]
        salida[i : i + len(bloque)] = dijkstra(matriz_dispersa, directed=True, indices=bloque)[:, fuentes]
    return salida


def calcular_matrices(puntos, grafo: Grafo | None, factor_velocidad: float, umbral_m: float = UMBRAL_SNAP_M) -> Matrices:
    """Matrices (n × n) de distancia (m) y tiempo (s) entre los puntos (lat, lon).

    - Con grafo: camino más corto por calles; cada punto se asigna a su nodo más cercano y se suman
      los tramos de acceso. Es asimétrica si hay calles de sentido único.
    - Los puntos a más de `umbral_m` de una calle, y todos los puntos si no hay grafo, usan
      línea recta × 1.35.
    El tiempo usa la velocidad base de cada tipo de vía dividida por `factor_velocidad`.
    """
    puntos = np.asarray(puntos, dtype=np.float64).reshape(-1, 2)
    n = len(puntos)
    recta = distancias_rectas(puntos) if n else np.zeros((0, 0))
    aprox_d = recta * FACTOR_RECTA
    aprox_t = aprox_d / (VELOCIDAD_APROX_KMH / 3.6 * factor_velocidad)
    if grafo is None or n == 0:
        return Matrices(aprox_d, aprox_t, "aproximada", list(range(n)))

    nodos, acceso_m = grafo.nodo_mas_cercano(puntos)
    resuelto = acceso_m <= umbral_m
    if not resuelto.any():
        return Matrices(aprox_d, aprox_t, "aproximada", list(range(n)))

    unicos, inverso = np.unique(nodos[resuelto], return_inverse=True)
    dist_u = _por_bloques(grafo.por_distancia, unicos)
    tiempo_u = _por_bloques(grafo.por_tiempo, unicos) / factor_velocidad

    # Posición de cada punto resuelto dentro de `unicos`; los no resueltos apuntan a 0 y se descartan después
    pos = np.zeros(n, dtype=np.int64)
    pos[resuelto] = inverso
    acceso = np.where(resuelto, acceso_m, 0.0)
    suma_acceso = acceso[:, None] + acceso[None, :]
    distancia = dist_u[np.ix_(pos, pos)] + suma_acceso
    tiempo = tiempo_u[np.ix_(pos, pos)] + suma_acceso / (VELOCIDAD_ACCESO_KMH / 3.6 * factor_velocidad)

    usar_aprox = ~(resuelto[:, None] & resuelto[None, :]) | ~np.isfinite(distancia) | ~np.isfinite(tiempo)
    distancia = np.where(usar_aprox, aprox_d, distancia)
    tiempo = np.where(usar_aprox, aprox_t, tiempo)
    np.fill_diagonal(distancia, 0.0)
    np.fill_diagonal(tiempo, 0.0)

    aproximados = [int(i) for i in np.flatnonzero(~resuelto)]
    fuente = "calles" if not aproximados else "mixta"
    return Matrices(distancia, tiempo, fuente, aproximados)


class RedVial:
    """Punto de entrada del módulo: carga el grafo una vez y calcula matrices con un factor de velocidad."""

    def __init__(self, grafo: Grafo | None, factor_velocidad: float):
        self.grafo = grafo
        self.factor_velocidad = factor_velocidad

    @classmethod
    def cargar(cls, factor_velocidad: float, ruta: Path | None = None) -> "RedVial":
        return cls(cargar_grafo(ruta), factor_velocidad)

    def matrices(self, puntos) -> Matrices:
        return calcular_matrices(puntos, self.grafo, self.factor_velocidad)
