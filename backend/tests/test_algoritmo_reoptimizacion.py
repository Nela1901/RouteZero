"""Pruebas del motor para re-optimizar rutas en curso (HU-012): arranque desde un punto y hora, pares fijos
y partida desde el plan vigente. No usan base de datos."""

import numpy as np

from src.algoritmo.construccion import evaluar_solucion
from src.algoritmo.evaluacion import ContextoPar, Datos, simular_ruta
from src.algoritmo.modelo import Arranque, Par, Pedido, Problema
from src.algoritmo.motor import resolver
from tests.ayudas_algoritmo import hora, problema_aleatorio

AHORA_S = hora(10)


def _plan_inicial():
    """Plan completo de la jornada y el problema del que sale."""
    problema = problema_aleatorio(n_pedidos=24, n_vehiculos=3, semilla=7, tiempo_max_s=None)
    return problema, resolver(problema)


def _reoptimizar(problema, resultado, nuevos: list[Pedido] | None = None, tiempo_s=None):
    """Arma el problema de re-optimización a las 10:00: la primera parada de cada ruta ya se entregó (el vehículo
    queda en ese punto) y el resto del plan sigue vigente."""
    entregados = {r.itinerario.paradas[0].pedido_id for r in resultado.rutas}
    indice = {x.id: i for i, x in enumerate(problema.pedidos)}
    restantes = [x for x in problema.pedidos if x.id not in entregados]
    nodos = [0] + [indice[x.id] + 1 for x in restantes]
    arranques, plan, pares = {}, {}, []
    for r in resultado.rutas:
        origen = indice[r.itinerario.paradas[0].pedido_id] + 1
        arranques[r.par.vehiculo.id] = Arranque(len(nodos), AHORA_S)
        nodos.append(origen)
        plan[r.par.vehiculo.id] = [p.pedido_id for p in r.itinerario.paradas[1:]]
        pares.append(r.par)
    nodos = np.array(nodos)
    p = problema.parametros
    p.tiempo_max_s = tiempo_s
    nuevos = nuevos or []
    return Problema(
        restantes + nuevos, problema.vehiculos, problema.conductores,
        problema.distancia_m[np.ix_(nodos, nodos)], problema.tiempo_s[np.ix_(nodos, nodos)], p,
        pares_fijos=pares, arranques=arranques, plan_vigente=plan,
    ), entregados


def test_un_vehiculo_en_ruta_parte_de_su_punto_y_a_la_hora_indicada():
    problema, resultado = _plan_inicial()
    nuevo, _ = _reoptimizar(problema, resultado)
    d = Datos(nuevo)
    par = nuevo.pares_fijos[0]
    ctx = ContextoPar.crear(par, nuevo.parametros, nuevo.arranques[par.vehiculo.id])
    desde_deposito = ContextoPar.crear(par, nuevo.parametros)
    itinerario = simular_ruta([0], ctx, d)
    assert ctx.nodo_inicio > 0
    assert itinerario.salida_s == AHORA_S
    # el primer tramo sale del punto del vehículo, no del depósito
    assert itinerario.distancia_m != simular_ruta([0], desde_deposito, d).distancia_m


def test_la_reoptimizacion_atiende_cada_pedido_restante_una_sola_vez_con_los_pares_ya_asignados():
    problema, resultado = _plan_inicial()
    nuevo, entregados = _reoptimizar(problema, resultado)
    nuevo_resultado = resolver(nuevo)
    paradas = [p.pedido_id for r in nuevo_resultado.rutas for p in r.itinerario.paradas]
    sin = [s.pedido_id for s in nuevo_resultado.sin_cobertura]
    assert sorted(paradas + sin) == sorted(x.id for x in nuevo.pedidos)
    assert not set(paradas) & entregados
    assert {r.par.vehiculo.id for r in nuevo_resultado.rutas} <= {par.vehiculo.id for par in nuevo.pares_fijos}
    assert all(r.itinerario.salida_s >= AHORA_S for r in nuevo_resultado.rutas)
    assert all(r.itinerario.valida for r in nuevo_resultado.rutas)


def test_la_reoptimizacion_nunca_es_peor_que_el_plan_vigente():
    problema, resultado = _plan_inicial()
    nuevo, _ = _reoptimizar(problema, resultado)
    d = Datos(nuevo)
    contextos = [ContextoPar.crear(par, nuevo.parametros, nuevo.arranques[par.vehiculo.id]) for par in nuevo.pares_fijos]
    indice = {x.id: i for i, x in enumerate(nuevo.pedidos)}
    rutas = [(k, [indice[i] for i in nuevo.plan_vigente[par.vehiculo.id]]) for k, par in enumerate(nuevo.pares_fijos)]
    costo_vigente = evaluar_solucion(d, contextos, rutas, []).costo
    assert resolver(nuevo).costo <= costo_vigente + 1e-6


def test_un_pedido_urgente_nuevo_se_integra_al_plan_en_curso():
    problema, resultado = _plan_inicial()
    urgente = Pedido("URGENTE", 10.0, "EXPRESS", hora(10), hora(13))
    nuevo, _ = _reoptimizar(problema, resultado)
    # el pedido nuevo se ubica en el mismo punto que el pedido 0 (misma fila y columna de la matriz)
    nodos = list(range(nuevo.distancia_m.shape[0]))
    nodos.insert(1 + len(nuevo.pedidos), 1)
    nodos = np.array(nodos)
    con_urgente = Problema(
        nuevo.pedidos + [urgente], nuevo.vehiculos, nuevo.conductores,
        nuevo.distancia_m[np.ix_(nodos, nodos)], nuevo.tiempo_s[np.ix_(nodos, nodos)], nuevo.parametros,
        pares_fijos=nuevo.pares_fijos,
        # los arranques apuntan al final de la matriz: se desplazan una posición por el nodo insertado
        arranques={k: Arranque(a.nodo + 1, a.salida_s) for k, a in nuevo.arranques.items()},
        plan_vigente=nuevo.plan_vigente,
    )
    r = resolver(con_urgente)
    atendidos = {p.pedido_id for ruta in r.rutas for p in ruta.itinerario.paradas}
    assert "URGENTE" in atendidos
    assert all(ruta.itinerario.valida for ruta in r.rutas)


def test_un_incidente_que_triplica_los_tiempos_no_rompe_la_solucion():
    problema, resultado = _plan_inicial()
    nuevo, _ = _reoptimizar(problema, resultado)
    lento = Problema(
        nuevo.pedidos, nuevo.vehiculos, nuevo.conductores, nuevo.distancia_m, nuevo.tiempo_s * 3.0, nuevo.parametros,
        pares_fijos=nuevo.pares_fijos, arranques=nuevo.arranques, plan_vigente=nuevo.plan_vigente,
    )
    r = resolver(lento)
    paradas = [p.pedido_id for ruta in r.rutas for p in ruta.itinerario.paradas]
    sin = [s.pedido_id for s in r.sin_cobertura]
    assert sorted(paradas + sin) == sorted(x.id for x in lento.pedidos)
    assert all(ruta.itinerario.valida for ruta in r.rutas)


def test_sin_pedidos_restantes_no_hay_nada_que_reoptimizar():
    problema, resultado = _plan_inicial()
    nuevo, _ = _reoptimizar(problema, resultado)
    vacio = Problema([], nuevo.vehiculos, nuevo.conductores, nuevo.distancia_m, nuevo.tiempo_s, nuevo.parametros,
                     pares_fijos=nuevo.pares_fijos, arranques=nuevo.arranques)
    r = resolver(vacio)
    assert r.rutas == []
    assert r.mensaje


def test_los_pares_fijos_no_se_vuelven_a_emparejar():
    problema, resultado = _plan_inicial()
    nuevo, _ = _reoptimizar(problema, resultado)
    par_otro = Par(nuevo.pares_fijos[0].vehiculo, nuevo.pares_fijos[1].conductor)
    problema_fijo = Problema(
        nuevo.pedidos, nuevo.vehiculos, nuevo.conductores, nuevo.distancia_m, nuevo.tiempo_s, nuevo.parametros,
        pares_fijos=[par_otro], arranques={par_otro.vehiculo.id: nuevo.arranques[par_otro.vehiculo.id]},
    )
    r = resolver(problema_fijo)
    assert all(ruta.par is par_otro for ruta in r.rutas)
