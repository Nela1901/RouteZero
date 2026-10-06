"""Red vial (spec `road-network`): matrices por calles reales con sentidos únicos, asignación al nodo más
cercano, respaldo en línea recta, tiempo por tipo de vía y rendimiento.

Las pruebas unitarias usan grafos sintéticos pequeños; las del grafo real se omiten si el archivo no existe.
"""

import random
import time
import tracemalloc

import numpy as np
import pytest

from src.red_vial.grafo import RUTA_POR_DEFECTO, Grafo, cargar_grafo
from src.red_vial.matrices import FACTOR_RECTA, RedVial, calcular_matrices, distancias_rectas

DEPOSITO = (-12.043632, -75.226373)
PLAZA_CONSTITUCION = (-12.0653, -75.2049)


def grafo_sintetico(coords, aristas) -> Grafo:
    """`aristas`: (origen, destino, km/h). La longitud sale de las coordenadas; son tramos de un solo sentido."""
    recta = distancias_rectas(coords)
    u = [a for a, _, _ in aristas]
    v = [b for _, b, _ in aristas]
    dist = [recta[a, b] for a, b, _ in aristas]
    seg = [recta[a, b] / (kmh / 3.6) for a, b, kmh in aristas]
    return Grafo(coords, u, v, dist, seg)


# Triángulo A -> B -> C -> A de un solo sentido (B no puede volver directo a A)
A, B, C = (-12.0600, -75.2100), (-12.0600, -75.2000), (-12.0500, -75.2050)


@pytest.fixture
def triangulo() -> Grafo:
    return grafo_sintetico([A, B, C], [(0, 1, 40), (1, 2, 40), (2, 0, 40)])


def test_la_matriz_por_calles_respeta_el_sentido_unico(triangulo):
    m = calcular_matrices([A, B, C], triangulo, factor_velocidad=1.0)
    recta = distancias_rectas([A, B, C])
    assert m.fuente == "calles"
    assert m.puntos_aproximados == []
    assert m.distancia_m[0, 1] == pytest.approx(recta[0, 1], rel=1e-6)
    # B -> A no existe directo: debe dar la vuelta B -> C -> A
    assert m.distancia_m[1, 0] == pytest.approx(recta[1, 2] + recta[2, 0], rel=1e-6)
    assert m.distancia_m[1, 0] > m.distancia_m[0, 1]


def test_la_matriz_tiene_la_forma_correcta_y_diagonal_cero(triangulo):
    m = calcular_matrices([A, B, C], triangulo, factor_velocidad=1.0)
    assert m.distancia_m.shape == (3, 3) == m.tiempo_s.shape
    assert np.all(np.diag(m.distancia_m) == 0) and np.all(np.diag(m.tiempo_s) == 0)
    assert np.isfinite(m.distancia_m).all() and np.isfinite(m.tiempo_s).all()


def test_dos_pedidos_en_el_mismo_lugar_no_dan_error(triangulo):
    m = calcular_matrices([A, A, B], triangulo, factor_velocidad=1.0)
    assert m.distancia_m[0, 1] == pytest.approx(0.0, abs=1e-6)
    assert m.distancia_m[0, 2] == pytest.approx(m.distancia_m[1, 2])


def test_un_punto_cerca_de_la_calle_suma_su_tramo_de_acceso(triangulo):
    cerca_de_a = (A[0] + 0.0009, A[1])  # unos 100 m al norte de A
    m = calcular_matrices([cerca_de_a, B], triangulo, factor_velocidad=1.0)
    acceso = distancias_rectas([cerca_de_a, A])[0, 1]
    base = calcular_matrices([A, B], triangulo, factor_velocidad=1.0).distancia_m[0, 1]
    assert m.fuente == "calles"
    # el tramo de acceso se mide en una proyección plana: difiere de la fórmula esférica en decímetros
    assert m.distancia_m[0, 1] == pytest.approx(base + acceso, rel=1e-3)


def test_archivo_ausente_usa_el_respaldo_en_linea_recta(tmp_path):
    red = RedVial.cargar(0.6, tmp_path / "no_existe.npz")
    assert red.grafo is None
    m = red.matrices([DEPOSITO, PLAZA_CONSTITUCION])
    assert m.fuente == "aproximada"
    assert m.distancia_m[0, 1] == pytest.approx(distancias_rectas([DEPOSITO, PLAZA_CONSTITUCION])[0, 1] * FACTOR_RECTA)


def test_archivo_danado_usa_el_respaldo(tmp_path):
    danado = tmp_path / "danado.npz"
    danado.write_bytes(b"esto no es un archivo npz")
    assert cargar_grafo(danado) is None
    assert RedVial.cargar(0.6, danado).matrices([DEPOSITO, PLAZA_CONSTITUCION]).fuente == "aproximada"


def test_un_punto_a_mas_de_500_m_de_la_red_usa_linea_recta(triangulo):
    lejos = (A[0] - 0.05, A[1])  # unos 5.5 km al sur de la red
    m = calcular_matrices([A, B, lejos], triangulo, factor_velocidad=1.0)
    recta = distancias_rectas([A, B, lejos])
    assert m.fuente == "mixta"
    assert m.puntos_aproximados == [2]
    assert m.distancia_m[0, 2] == pytest.approx(recta[0, 2] * FACTOR_RECTA)
    assert m.distancia_m[2, 1] == pytest.approx(recta[2, 1] * FACTOR_RECTA)
    assert m.distancia_m[0, 1] == pytest.approx(recta[0, 1], rel=1e-6)  # el resto sigue por calles


def test_todos_los_puntos_lejos_de_la_red_se_marcan_aproximados(triangulo):
    lejos = [(A[0] - 0.05, A[1]), (A[0] - 0.06, A[1])]
    m = calcular_matrices(lejos, triangulo, factor_velocidad=1.0)
    assert m.fuente == "aproximada" and m.puntos_aproximados == [0, 1]


def test_la_avenida_es_mas_rapida_que_la_calle_residencial():
    # Dos pares de nodos con la misma separación: uno por avenida (60 km/h) y otro por calle residencial (30)
    coords = [(-12.06, -75.21), (-12.06, -75.20), (-12.05, -75.21), (-12.05, -75.20)]
    g = grafo_sintetico(coords, [(0, 1, 60), (2, 3, 30)])
    m = calcular_matrices([coords[0], coords[1], coords[2], coords[3]], g, factor_velocidad=1.0)
    assert m.distancia_m[0, 1] == pytest.approx(m.distancia_m[2, 3], rel=1e-3)
    assert m.tiempo_s[0, 1] < m.tiempo_s[2, 3]
    assert m.tiempo_s[2, 3] == pytest.approx(2 * m.tiempo_s[0, 1], rel=1e-3)


def test_el_factor_de_velocidad_escala_los_tiempos(triangulo):
    libre = calcular_matrices([A, B, C], triangulo, factor_velocidad=1.0)
    lento = calcular_matrices([A, B, C], triangulo, factor_velocidad=0.5)
    assert lento.tiempo_s[0, 1] == pytest.approx(2 * libre.tiempo_s[0, 1], rel=1e-6)
    assert lento.distancia_m[0, 1] == pytest.approx(libre.distancia_m[0, 1])


def test_si_hay_varios_tramos_entre_los_mismos_nodos_se_usa_el_mas_corto():
    coords = [A, B]
    g = Grafo(coords, [0, 0], [1, 1], [1000.0, 700.0], [100.0, 50.0])
    assert g.por_distancia[0, 1] == 700.0 and g.por_tiempo[0, 1] == 50.0


def test_la_carga_del_grafo_es_unica_por_proceso():
    if not RUTA_POR_DEFECTO.exists():
        pytest.skip("No existe data/huancayo_grafo.npz")
    assert cargar_grafo() is cargar_grafo()


# ----------------------------------------------------------------------------- grafo real de Huancayo

requiere_grafo = pytest.mark.skipif(not RUTA_POR_DEFECTO.exists(), reason="No existe data/huancayo_grafo.npz")


def puntos_aleatorios(n: int, semilla: int = 7) -> list[tuple[float, float]]:
    azar = random.Random(semilla)
    return [DEPOSITO] + [(azar.uniform(-12.10, -12.00), azar.uniform(-75.26, -75.18)) for _ in range(n)]


@requiere_grafo
def test_el_deposito_y_la_plaza_estan_a_menos_de_500_m_de_una_calle():
    grafo = cargar_grafo()
    _, acceso = grafo.nodo_mas_cercano([DEPOSITO, PLAZA_CONSTITUCION])
    assert (acceso < 500).all()


@requiere_grafo
def test_el_grafo_real_da_distancias_coherentes_con_la_linea_recta():
    puntos = puntos_aleatorios(30)
    m = RedVial.cargar(0.6).matrices(puntos)
    recta = distancias_rectas(puntos)
    pares = ~np.eye(len(puntos), dtype=bool) & (recta > 500)
    razon = m.distancia_m[pares] / recta[pares]
    assert m.fuente in ("calles", "mixta")
    assert np.isfinite(m.distancia_m).all() and np.isfinite(m.tiempo_s).all()
    assert (razon >= 0.98).all()  # por calles nunca es más corto que la línea recta
    assert 1.1 < razon.mean() < 1.8  # medido en Huancayo: ~1.38


@requiere_grafo
def test_las_tres_avenidas_de_los_requisitos_estan_en_el_grafo():
    grafo = cargar_grafo()
    nombres = [str(n).lower() for n in grafo.nombres]
    for clave in ("ferrocarril", "giraldez", "calle real"):
        ids = [i for i, n in enumerate(nombres) if clave in n]
        assert ids and np.isin(grafo.nombre_id, ids).any(), clave


@requiere_grafo
@pytest.mark.benchmark
def test_rendimiento_de_la_matriz_de_150_pedidos_y_el_deposito():
    """Spec `road-network`: 151 × 151 en menos de 5 s y con menos de 100 MB adicionales."""
    red = RedVial.cargar(0.6)
    puntos = puntos_aleatorios(150)
    tracemalloc.start()
    inicio = time.perf_counter()
    m = red.matrices(puntos)
    duracion = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"\nmatriz 151x151: {duracion:.2f} s, pico adicional {pico / 1e6:.0f} MB, fuente {m.fuente}")
    assert m.distancia_m.shape == (151, 151)
    assert duracion < 5.0
    assert pico < 100e6
