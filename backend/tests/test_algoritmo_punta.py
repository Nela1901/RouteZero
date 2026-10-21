"""Tiempos de viaje por franja horaria (RF-003, hora punta): un tramo usa la matriz de hora punta si sale dentro de
una franja. Sin franjas o sin esa matriz, el motor se comporta como antes. No usan base de datos."""

import numpy as np

from src.algoritmo.construccion import evaluar_solucion
from src.algoritmo.evaluacion import ContextoPar, Datos, simular_ruta
from src.algoritmo.modelo import Par
from src.algoritmo.motor import resolver
from tests.ayudas_algoritmo import hora, problema_aleatorio

PUNTA = ((hora(8), hora(9)),)  # 08:00-09:00


def _con_punta(factor: float = 2.0, franjas=PUNTA, **kwargs):
    p = problema_aleatorio(n_pedidos=12, n_vehiculos=2, semilla=3, tiempo_max_s=None, **kwargs)
    p.tiempo_punta_s = p.tiempo_s * factor
    p.parametros.franjas_punta = franjas
    return p


def _contexto(p):
    par = Par(p.vehiculos[0], p.conductores[0])
    return ContextoPar.crear(par, p.parametros), Datos(p)


def test_un_tramo_que_sale_en_hora_punta_usa_la_matriz_de_punta():
    p = _con_punta(2.0)
    ctx, d = _contexto(p)
    itinerario = simular_ruta([0], ctx, d)
    # sale a las 08:00 (dentro de la franja): el viaje de ida dura el doble que el de la matriz normal
    assert itinerario.paradas[0].llegada_s == ctx.salida_s + 2.0 * p.tiempo_s[0, 1]


def test_un_tramo_que_sale_fuera_de_la_franja_usa_la_matriz_normal():
    p = _con_punta(2.0, franjas=((hora(10), hora(11)),))
    ctx, d = _contexto(p)
    itinerario = simular_ruta([0], ctx, d)
    assert itinerario.paradas[0].llegada_s == ctx.salida_s + p.tiempo_s[0, 1]


def test_el_siguiente_tramo_depende_de_la_hora_a_la_que_sale():
    p = _con_punta(3.0, franjas=((hora(7), hora(8) + 600),))  # termina 08:10: la atención del primero dura 10 min
    ctx, d = _contexto(p)
    it = simular_ruta([0, 1], ctx, d)
    primera = it.paradas[0]
    sale_segunda = max(primera.llegada_s, p.pedidos[0].ventana_inicio_s) + p.parametros.atencion_s
    esperado = sale_segunda + (3.0 if sale_segunda < hora(8) + 600 else 1.0) * p.tiempo_s[1, 2]
    assert it.paradas[1].llegada_s == esperado


def test_sin_franjas_o_sin_matriz_de_punta_el_resultado_es_el_de_siempre():
    base = problema_aleatorio(n_pedidos=12, n_vehiculos=2, semilla=3, tiempo_max_s=None)
    sin_franjas = _con_punta(3.0, franjas=())
    sin_matriz = problema_aleatorio(n_pedidos=12, n_vehiculos=2, semilla=3, tiempo_max_s=None)
    sin_matriz.parametros.franjas_punta = PUNTA
    esperado = resolver(base).costo
    assert resolver(sin_franjas).costo == esperado
    assert resolver(sin_matriz).costo == esperado


def test_con_hora_punta_las_rutas_son_validas_y_no_terminan_antes():
    base = resolver(problema_aleatorio(n_pedidos=24, n_vehiculos=3, semilla=5, tiempo_max_s=None))
    p = problema_aleatorio(n_pedidos=24, n_vehiculos=3, semilla=5, tiempo_max_s=None)
    p.tiempo_punta_s = p.tiempo_s * 2.0
    p.parametros.franjas_punta = ((hora(8), hora(10)), (hora(12), hora(14)))
    r = resolver(p)
    atendidos = [x.pedido_id for ruta in r.rutas for x in ruta.itinerario.paradas]
    sin = [s.pedido_id for s in r.sin_cobertura]
    assert sorted(atendidos + sin) == sorted(x.id for x in p.pedidos)
    assert all(ruta.itinerario.valida for ruta in r.rutas)
    # congestionar el tráfico no puede abaratar la jornada
    assert r.costo >= base.costo - 1e-6


def test_la_construccion_y_la_simulacion_coinciden_con_franjas_activas():
    """El ACO arma rutas con una versión vectorizada de las reglas; si no coincidiera con `simular_ruta`, esas rutas
    saldrían inválidas y se descartarían. Con franjas y descansos de por medio, ninguna debe descartarse."""
    p = problema_aleatorio(n_pedidos=30, n_vehiculos=3, semilla=11, tiempo_max_s=None, jornada_max_s=8 * 3600)
    p.tiempo_punta_s = p.tiempo_s * 2.5
    p.parametros.franjas_punta = ((hora(7.5), hora(9.5)), (hora(12), hora(14.5)))
    p.parametros.descanso_cada_s = 2 * 3600  # fuerza descansos dentro de la jornada
    d = Datos(p)
    from src.algoritmo.construccion import construir

    contextos = [ContextoPar.crear(Par(v, c), p.parametros) for v, c in zip(p.vehiculos, p.conductores)]
    rutas, sin = construir(d, contextos, None, np.random.default_rng(0))
    solucion = evaluar_solucion(d, contextos, rutas, sin)
    assert len(solucion.rutas) == len(rutas)  # ninguna ruta armada se descartó por inválida
