"""Grafo de calles dirigido de Huancayo (datos © OpenStreetMap contributors, licencia ODbL).

Lo genera `scripts/generar_grafo.py` y se guarda en `data/huancayo_grafo.npz`. Este módulo solo lo
carga y responde dos preguntas: cuál es el nodo de calle más cercano a un punto y cuál es el camino más
corto entre nodos. No depende de FastAPI ni de la base de datos.
"""

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

RUTA_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data" / "huancayo_grafo.npz"
METROS_POR_GRADO = 111_320.0


def _csr_minimo(u: np.ndarray, v: np.ndarray, peso: np.ndarray, n: int) -> csr_matrix:
    """Matriz dispersa que, si hay varios tramos entre el mismo par de nodos, conserva el de menor peso
    (por defecto scipy sumaría los duplicados, lo que falsearía las distancias)."""
    orden = np.lexsort((peso, v, u))
    u, v, peso = u[orden], v[orden], peso[orden]
    primero = np.ones(len(u), dtype=bool)
    primero[1:] = (u[1:] != u[:-1]) | (v[1:] != v[:-1])
    return csr_matrix((peso[primero], (u[primero], v[primero])), shape=(n, n))


class Grafo:
    def __init__(self, coords, u, v, dist, seg, nombre_id=None, nombres=None):
        self.coords = np.asarray(coords, dtype=np.float64)
        self.n = len(self.coords)
        u = np.asarray(u, dtype=np.int64)
        v = np.asarray(v, dtype=np.int64)
        self.dist = np.asarray(dist, dtype=np.float64)
        self.seg = np.asarray(seg, dtype=np.float64)
        self.nombre_id = np.zeros(len(u), dtype=np.int32) if nombre_id is None else np.asarray(nombre_id)
        self.nombres = np.array([""]) if nombres is None else np.asarray(nombres)
        self.u, self.v = u, v
        self.por_distancia = _csr_minimo(u, v, self.dist, self.n)
        self.por_tiempo = _csr_minimo(u, v, self.seg, self.n)
        # Proyección plana (metros) alrededor de la latitud media: suficiente a escala de ciudad.
        self._coseno = math.cos(math.radians(float(self.coords[:, 0].mean())))
        self._arbol = cKDTree(self._proyectar(self.coords))

    def _proyectar(self, puntos: np.ndarray) -> np.ndarray:
        puntos = np.asarray(puntos, dtype=np.float64)
        return np.column_stack((puntos[:, 1] * self._coseno, puntos[:, 0])) * METROS_POR_GRADO

    def nodo_mas_cercano(self, puntos) -> tuple[np.ndarray, np.ndarray]:
        """Nodo más cercano a cada punto (lat, lon) y su distancia en metros."""
        distancias, nodos = self._arbol.query(self._proyectar(np.asarray(puntos)))
        return nodos, distancias

    @classmethod
    def desde_archivo(cls, ruta: Path) -> "Grafo":
        with np.load(ruta, allow_pickle=False) as datos:
            return cls(
                datos["coords"], datos["u"], datos["v"], datos["dist"], datos["seg"],
                datos["nombre_id"], datos["nombres"],
            )


@lru_cache(maxsize=4)
def _grafo_cargado(ruta: str) -> Grafo:
    return Grafo.desde_archivo(Path(ruta))


def cargar_grafo(ruta: Path | None = None) -> Grafo | None:
    """Carga el grafo una sola vez por proceso. Devuelve None si el archivo falta o está dañado, para
    que el sistema continúe con el respaldo en línea recta."""
    try:
        return _grafo_cargado(str(ruta or RUTA_POR_DEFECTO))
    except Exception:  # noqa: BLE001 - cualquier fallo de lectura activa el respaldo
        return None
