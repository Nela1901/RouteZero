"""Trazado por calles de una ruta (HU-013): el camino más rápido entre paradas consecutivas sobre el grafo de Huancayo.

No depende de FastAPI ni de la base de datos: recibe puntos y horas de salida y devuelve, por tramo, la línea a
dibujar, la distancia y el tiempo estimado. Cada tramo usa la matriz de tiempos que corresponde a la hora en que sale
(hora punta o no) y los incidentes vigentes, igual que el motor, para que lo dibujado coincida con lo planificado."""

import math
from functools import lru_cache

import numpy as np
from scipy.sparse.csgraph import dijkstra

from src.red_vial.grafo import Grafo
from src.red_vial.matrices import FACTOR_RECTA, UMBRAL_SNAP_M, VELOCIDAD_ACCESO_KMH, VELOCIDAD_APROX_KMH, distancias_rectas
from src.rutas import congestion

EPSILON_SIMPLIFICACION_M = 3.0  # se descartan los puntos que desvían la línea menos que esto
METROS_POR_GRADO = 111_320.0


def _plano(puntos: np.ndarray) -> np.ndarray:
    """Proyección plana en metros alrededor de la latitud media (suficiente a escala de ciudad)."""
    coseno = math.cos(math.radians(float(puntos[:, 0].mean())))
    return np.column_stack((puntos[:, 1] * coseno, puntos[:, 0])) * METROS_POR_GRADO


def simplificar(puntos: np.ndarray, epsilon_m: float = EPSILON_SIMPLIFICACION_M) -> np.ndarray:
    """Douglas-Peucker: quita los puntos casi alineados. Siempre conserva el primero y el último."""
    n = len(puntos)
    if n <= 2:
        return puntos
    xy = _plano(puntos)
    conservar = np.zeros(n, dtype=bool)
    conservar[0] = conservar[-1] = True
    pila = [(0, n - 1)]
    while pila:
        a, b = pila.pop()
        if b - a < 2:
            continue
        pa, pb = xy[a], xy[b]
        d = pb - pa
        largo = float(np.hypot(*d))
        tramo = xy[a + 1 : b]
        if largo < 1e-9:
            dist = np.hypot(*(tramo - pa).T)
        else:
            dist = np.abs(d[0] * (pa[1] - tramo[:, 1]) - (pa[0] - tramo[:, 0]) * d[1]) / largo
        k = int(np.argmax(dist))
        if dist[k] > epsilon_m:
            medio = a + 1 + k
            conservar[medio] = True
            pila.extend([(a, medio), (medio, b)])
    return puntos[conservar]


def longitud_km(puntos: np.ndarray) -> float:
    if len(puntos) < 2:
        return 0.0
    return float(np.hypot(*np.diff(_plano(puntos), axis=0).T).sum()) / 1000.0


@lru_cache(maxsize=16)
def _matriz_de_tiempos(grafo: Grafo, factores: tuple | None):
    """CSR de tiempos con la congestión indicada; se reutiliza entre rutas y peticiones."""
    return grafo.tiempo_con_congestion(dict(factores) if factores else None)


def _recto(a, b, factor_velocidad: float) -> tuple[np.ndarray, float]:
    puntos = np.array([a, b], dtype=float)
    metros = float(distancias_rectas(puntos)[0, 1]) * FACTOR_RECTA
    return puntos, metros / (VELOCIDAD_APROX_KMH / 3.6 * factor_velocidad) / 60.0


def trazar(
    grafo: Grafo | None, puntos: list, salidas_s: list[float], incidentes: list[dict], factor_velocidad: float, con_nodos: bool = False
) -> list[dict]:
    """Un tramo por cada par de puntos consecutivos. `salidas_s[i]` es la hora (segundos desde la medianoche) a la
    que sale el tramo i. Cada tramo trae `puntos` ([lat, lon]), `distancia_km`, `duracion_min` y `en_punta`. Con
    `con_nodos`, también `nodos`: los nodos del grafo por los que pasa (la línea dibujada se simplifica y los pierde)."""
    n = len(puntos)
    if n < 2:
        return []
    coords = np.asarray(puntos, dtype=float)
    nodos = acceso = None
    if grafo is not None:
        nodos, acceso = grafo.nodo_mas_cercano(coords)

    # Se agrupan los tramos por matriz de tiempos para resolver cada grupo con una sola pasada de Dijkstra
    grupos: dict[tuple | None, list[int]] = {}
    for i in range(n - 1):
        factores = congestion.factores_de_la_hora(incidentes, salidas_s[i])
        clave = tuple(sorted(factores.items())) if factores else None
        grupos.setdefault(clave, []).append(i)

    resultado: list[dict | None] = [None] * (n - 1)
    for clave, tramos in grupos.items():
        resueltos = [i for i in tramos if grafo is not None and acceso[i] <= UMBRAL_SNAP_M and acceso[i + 1] <= UMBRAL_SNAP_M]
        if resueltos:
            fuentes = sorted({int(nodos[i]) for i in resueltos})
            fila = {f: k for k, f in enumerate(fuentes)}
            tiempos, anteriores = dijkstra(_matriz_de_tiempos(grafo, clave), directed=True, indices=fuentes, return_predecessors=True)
        for i in tramos:
            punta = congestion.en_punta(salidas_s[i])
            origen, destino = coords[i], coords[i + 1]
            camino = None
            nodos_camino = []
            if i in resueltos:
                src, dst = int(nodos[i]), int(nodos[i + 1])
                k = fila[src]
                if src == dst:
                    nodos_camino = [src]
                elif np.isfinite(tiempos[k, dst]):
                    nodos_camino, actual = [dst], dst
                    while actual != src:
                        actual = int(anteriores[k, actual])
                        if actual < 0:
                            nodos_camino = None
                            break
                        nodos_camino.append(actual)
                    if nodos_camino is not None:
                        nodos_camino.reverse()
                else:
                    nodos_camino = None
                if nodos_camino is not None:
                    lineal = np.vstack([origen, grafo.coords[nodos_camino], destino])
                    segundos = (0.0 if src == dst else tiempos[k, dst]) / factor_velocidad
                    segundos += (acceso[i] + acceso[i + 1]) / (VELOCIDAD_ACCESO_KMH / 3.6 * factor_velocidad)
                    camino = (lineal, segundos / 60.0)
            if camino is None:  # sin calle cercana o sin camino: línea recta con la velocidad de respaldo
                lineal, minutos = _recto(origen, destino, factor_velocidad)
                camino = (lineal, minutos)
            lineal = simplificar(camino[0])
            resultado[i] = {
                **({"nodos": [int(n) for n in (nodos_camino or [])]} if con_nodos else {}),
                "puntos": [[round(float(la), 5), round(float(lo), 5)] for la, lo in lineal],
                "distancia_km": round(longitud_km(camino[0]), 3),
                "duracion_min": round(float(camino[1]), 1),
                "en_punta": punta,
            }
    return resultado  # type: ignore[return-value]
