"""Trazado por calles (HU-013) y niveles de congestión por hora punta (RF-003). No usan base de datos."""

import numpy as np
import pytest

from src.red_vial.grafo import Grafo
from src.red_vial.matrices import distancias_rectas
from src.rutas import congestion
from src.rutas.trazado import longitud_km, simplificar, trazar

A, B, C = (-12.0600, -75.2100), (-12.0600, -75.2000), (-12.0500, -75.2050)
DIEZ, OCHO_Y_MEDIA = 10 * 3600, 8 * 3600 + 1800


@pytest.fixture
def dos_caminos() -> Grafo:
    """A -> B directo por la Av. Giráldez, o A -> C -> B por un jirón más largo. Un solo sentido."""
    coords = [A, B, C]
    recta = distancias_rectas(coords)
    aristas = [(0, 1, 1), (0, 2, 2), (2, 1, 2)]
    u, v = [a for a, _, _ in aristas], [b for _, b, _ in aristas]
    dist = [recta[a, b] for a, b, _ in aristas]
    seg = [recta[a, b] / (40 / 3.6) for a, b, _ in aristas]
    return Grafo(coords, u, v, dist, seg, [1, 2, 2], ["", "Avenida Giraldez", "Jiron Otro"])


def incidente(calle, factor):
    return {"calle": calle, "factor": factor}


# ---------------------------------------------------------------------------------------- trazado
def test_el_tramo_sigue_la_calle_y_empalma_con_las_paradas(dos_caminos):
    [t] = trazar(dos_caminos, [A, B], [DIEZ], [], 1.0)
    assert t["puntos"][0] == [round(A[0], 5), round(A[1], 5)]
    assert t["puntos"][-1] == [round(B[0], 5), round(B[1], 5)]
    assert t["distancia_km"] == pytest.approx(distancias_rectas([A, B])[0, 1] / 1000, rel=0.01)
    assert t["duracion_min"] == pytest.approx(distancias_rectas([A, B])[0, 1] / (40 / 3.6) / 60, abs=0.1)
    assert t["en_punta"] is False


def test_un_incidente_hace_que_el_camino_rodee_la_calle_congestionada(dos_caminos):
    [directo] = trazar(dos_caminos, [A, B], [DIEZ], [], 1.0)
    [rodeo] = trazar(dos_caminos, [A, B], [DIEZ], [incidente("Av. Giráldez", 10.0)], 1.0)
    assert len(directo["puntos"]) == 2
    assert [round(C[0], 5), round(C[1], 5)] in rodeo["puntos"]  # pasa por C
    assert rodeo["distancia_km"] > directo["distancia_km"]


def test_en_hora_punta_el_tramo_tarda_mas_y_se_marca(dos_caminos):
    [fluido] = trazar(dos_caminos, [A, B], [DIEZ], [], 1.0)
    [punta] = trazar(dos_caminos, [A, B], [OCHO_Y_MEDIA], [], 1.0)
    assert punta["en_punta"] is True
    assert punta["duracion_min"] == pytest.approx(fluido["duracion_min"] * congestion.FACTOR_PUNTA["Av. Giráldez"], rel=0.02)
    assert punta["distancia_km"] == fluido["distancia_km"]  # el trazado directo sigue siendo el mejor


def test_cada_tramo_usa_la_matriz_de_su_hora_de_salida(dos_caminos):
    tramos = trazar(dos_caminos, [A, B, B], [DIEZ, OCHO_Y_MEDIA], [], 1.0)
    assert [t["en_punta"] for t in tramos] == [False, True]
    assert tramos[1]["distancia_km"] == 0.0  # mismo punto: no hay recorrido


def test_sin_camino_por_calles_se_usa_una_linea_recta(dos_caminos):
    [t] = trazar(dos_caminos, [B, A], [DIEZ], [], 1.0)  # el grafo es de un solo sentido: B no llega a A
    assert len(t["puntos"]) == 2 and t["distancia_km"] > 0 and t["duracion_min"] > 0


def test_sin_grafo_todos_los_tramos_son_rectos():
    tramos = trazar(None, [A, B, C], [DIEZ, DIEZ], [], 0.6)
    assert len(tramos) == 2 and all(len(t["puntos"]) == 2 for t in tramos)


def test_un_solo_punto_no_tiene_tramos(dos_caminos):
    assert trazar(dos_caminos, [A], [], [], 1.0) == []


def test_simplificar_quita_los_puntos_alineados_y_conserva_las_esquinas():
    linea = np.array([[0.0, 0.0], [0.0, 0.0005], [0.0, 0.001], [0.0005, 0.001], [0.001, 0.001]])
    simple = simplificar(linea, epsilon_m=3.0)
    assert simple.tolist() == [[0.0, 0.0], [0.0, 0.001], [0.001, 0.001]]
    assert longitud_km(simple) == pytest.approx(longitud_km(linea), rel=1e-6)


# ---------------------------------------------------------------------------------------- congestión
def test_niveles_verde_amarillo_y_rojo():
    assert congestion.nivel(1.0) == "VERDE"
    assert congestion.nivel(1.3) == "AMARILLO"
    assert congestion.nivel(1.99) == "AMARILLO"
    assert congestion.nivel(2.0) == "ROJO"
    assert congestion.nivel(5.4) == "ROJO"


def test_las_franjas_punta_son_las_de_rf_003():
    for hora, esperado in [(7.4, False), (7.5, True), (9.4, True), (9.5, False), (12.0, True), (14.4, True), (14.5, False),
                           (16.9, False), (17.0, True), (20.9, True), (21.0, False)]:
        assert congestion.en_punta(hora * 3600) is esperado, hora


def test_el_factor_efectivo_combina_hora_punta_e_incidente():
    assert congestion.factor_efectivo("Av. Ferrocarril", DIEZ, []) == (1.0, [])
    f, motivos = congestion.factor_efectivo("Av. Ferrocarril", OCHO_Y_MEDIA, [])
    assert f == congestion.FACTOR_PUNTA["Av. Ferrocarril"] and motivos == ["hora punta"]
    f, motivos = congestion.factor_efectivo("Av. Ferrocarril", DIEZ, [incidente("Av. Ferrocarril", 3.0)])
    assert f == 3.0 and motivos == ["incidente"]
    f, motivos = congestion.factor_efectivo("Av. Ferrocarril", OCHO_Y_MEDIA, [incidente("Av. Ferrocarril", 3.0)])
    assert f == pytest.approx(3.0 * congestion.FACTOR_PUNTA["Av. Ferrocarril"]) and motivos == ["hora punta", "incidente"]
    assert congestion.factor_efectivo("Calle Real", DIEZ, [incidente("Av. Ferrocarril", 3.0)])[0] == 1.0


def test_los_factores_para_las_matrices_separan_lo_normal_de_la_hora_punta():
    normal, punta = congestion.factores_de_matrices([])
    assert normal is None
    assert set(punta) == {"ferrocarril", "giraldez", "calle real"}
    normal, punta = congestion.factores_de_matrices([incidente("Calle Real", 2.0), incidente("Calle Real", 3.0)])
    assert normal == {"calle real": 3.0}  # se toma el mayor de los incidentes sobre la misma vía
    assert punta["calle real"] == pytest.approx(3.0 * congestion.FACTOR_PUNTA["Calle Real"])
    assert punta["ferrocarril"] == congestion.FACTOR_PUNTA["Av. Ferrocarril"]


# ---------------------------------------------------------------------------------------- HU-014: nodos de la ruta
def test_con_nodos_el_tramo_informa_los_nodos_por_los_que_pasa(dos_caminos):
    [t] = trazar(dos_caminos, [A, B], [DIEZ], [incidente("Av. Giráldez", 10.0)], 1.0, con_nodos=True)
    assert t["nodos"] == [0, 2, 1]  # A -> C -> B
    [sin] = trazar(dos_caminos, [A, B], [DIEZ], [], 1.0)
    assert "nodos" not in sin


def test_los_nodos_de_una_calle_sirven_para_saber_si_el_camino_la_cruza(dos_caminos):
    assert dos_caminos.nodos_de_calle("Giráldez") == frozenset({0, 1})
    assert dos_caminos.nodos_de_calle("jiron otro") == frozenset({0, 2, 1})
    assert dos_caminos.nodos_de_calle("no existe") == frozenset()
    [por_giraldez] = trazar(dos_caminos, [A, B], [DIEZ], [], 1.0, con_nodos=True)
    assert set(por_giraldez["nodos"]) & dos_caminos.nodos_de_calle("Giráldez")
