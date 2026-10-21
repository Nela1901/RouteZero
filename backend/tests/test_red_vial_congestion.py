"""Congestión por calle (RN-012): encarece el tiempo de las calles indicadas sin cambiar las distancias, y el
camino más rápido las rodea si conviene."""

import numpy as np
import pytest

from src.red_vial.grafo import RUTA_POR_DEFECTO, Grafo, cargar_grafo, normalizar_calle
from src.red_vial.matrices import calcular_matrices, distancias_rectas

A, B, C = (-12.0600, -75.2100), (-12.0600, -75.2000), (-12.0500, -75.2050)


@pytest.fixture
def dos_caminos() -> Grafo:
    """A -> B directo por la Av. Giráldez, o A -> C -> B por un jirón (más largo y a la misma velocidad)."""
    coords = [A, B, C]
    recta = distancias_rectas(coords)
    aristas = [(0, 1, "Avenida Giraldez"), (0, 2, "Jiron Otro"), (2, 1, "Jiron Otro")]
    u, v = [a for a, _, _ in aristas], [b for _, b, _ in aristas]
    dist = [recta[a, b] for a, b, _ in aristas]
    seg = [recta[a, b] / (40 / 3.6) for a, b, _ in aristas]
    nombres = ["", "Avenida Giraldez", "Jiron Otro"]
    ids = [1, 2, 2]
    return Grafo(coords, u, v, dist, seg, ids, nombres)


def test_sin_factores_se_usa_la_matriz_de_tiempos_base(dos_caminos):
    assert dos_caminos.tiempo_con_congestion(None) is dos_caminos.por_tiempo
    assert dos_caminos.tiempo_con_congestion({}) is dos_caminos.por_tiempo


def test_la_congestion_encarece_el_tiempo_pero_no_la_distancia(dos_caminos):
    base = calcular_matrices([A, B], dos_caminos, 1.0)
    con = calcular_matrices([A, B], dos_caminos, 1.0, congestion={"Giráldez": 10.0})
    assert con.distancia_m[0, 1] == pytest.approx(base.distancia_m[0, 1])
    assert con.tiempo_s[0, 1] > base.tiempo_s[0, 1]


def test_el_camino_mas_rapido_rodea_la_calle_congestionada(dos_caminos):
    recta = distancias_rectas([A, B, C])
    desvio_s = (recta[0, 2] + recta[2, 1]) / (40 / 3.6)
    con = calcular_matrices([A, B], dos_caminos, 1.0, congestion={"giraldez": 100.0})
    assert con.tiempo_s[0, 1] == pytest.approx(desvio_s, rel=1e-6)


def test_un_nombre_sin_coincidencias_no_cambia_nada(dos_caminos):
    base = calcular_matrices([A, B], dos_caminos, 1.0)
    con = calcular_matrices([A, B], dos_caminos, 1.0, congestion={"Calle Inexistente": 5.0})
    assert np.allclose(con.tiempo_s, base.tiempo_s)


def test_los_nombres_se_comparan_sin_tildes_ni_mayusculas():
    assert normalizar_calle("Av. Giráldez ") == "av. giraldez"
    assert normalizar_calle("CALLE REAL") == "calle real"


def test_los_tramos_de_una_calle_se_devuelven_para_dibujarlos(dos_caminos):
    tramos = dos_caminos.tramos_de_calle("giráldez")
    assert tramos == [[A, B]]
    assert dos_caminos.tramos_de_calle("no existe") == []


@pytest.mark.skipif(not RUTA_POR_DEFECTO.exists(), reason="no está el grafo real de Huancayo")
@pytest.mark.parametrize("calle", ["Ferrocarril", "Giráldez", "Calle Real"])
def test_el_grafo_real_trae_las_tres_calles_de_la_rn_012(calle):
    assert len(cargar_grafo().tramos_de_calle(calle)) > 0
