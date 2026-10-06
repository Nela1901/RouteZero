"""Motor de optimización (specs `route-optimization`): itinerarios, elegibilidad, solución voraz, ACO y
pedidos sin cobertura. No usa la base de datos: trabaja con problemas sintéticos.
"""

import time
from datetime import timedelta

import numpy as np
import pytest
from ayudas_algoritmo import FECHA, hora, problema_aleatorio

from src.algoritmo.construccion import solucion_voraz
from src.algoritmo.emparejamiento import emparejar, licencia_compatible
from src.algoritmo.evaluacion import ContextoPar, Datos, simular_ruta
from src.algoritmo.modelo import (
    FLOTA_INSUFICIENTE,
    FUERA_DE_JORNADA,
    PESO_EXCEDE_CAPACIDAD,
    SIN_RECURSOS,
    Conductor,
    Par,
    Parametros,
    Pedido,
    Problema,
    Vehiculo,
)
from src.algoritmo.motor import resolver

# --------------------------------------------------------------------------------------------- 4.1 itinerarios
#          depósito  A     B
T = np.array([[0, 600, 1200], [700, 0, 300], [900, 300, 0]], dtype=float)  # segundos; T[i][j] = de i a j
D = T * 10.0                                                                # metros

PEDIDO_A = Pedido("A", 20.0, "ESTANDAR", hora(8), hora(9))
PEDIDO_B = Pedido("B", 30.0, "ESTANDAR", hora(9), hora(10))
VEHICULO = Vehiculo("V1", "ABC-101", "CAMIONETA", 1000.0, 10.0, 0.25)
CONDUCTOR = Conductor("C1", "A-IIb", FECHA + timedelta(days=100), hora(6), hora(14))


def datos_y_contexto(pedidos, conductor=CONDUCTOR, vehiculo=VEHICULO, **parametros):
    problema = Problema(pedidos, [vehiculo], [conductor], D, T, Parametros(fecha=FECHA, **parametros))
    return Datos(problema), ContextoPar.crear(Par(vehiculo, conductor), problema.parametros)


def test_itinerario_con_espera_hasta_que_abre_la_ventana():
    d, ctx = datos_y_contexto([PEDIDO_A, PEDIDO_B])
    it = simular_ruta([0, 1], ctx, d)
    assert it.salida_s == hora(8)
    assert it.paradas[0].llegada_s == hora(8) + 600
    assert it.paradas[1].llegada_s == hora(8) + 600 + 600 + 300  # tras atender A
    assert it.paradas[1].inicio_atencion_s == hora(9)             # espera hasta las 09:00: sin penalización
    assert it.paradas[1].retraso_s == 0
    assert it.regreso_s == hora(9) + 600 + 900
    assert it.distancia_m == (600 + 300 + 900) * 10
    assert it.valida and it.descansos == 0


def test_la_entrega_tardia_se_penaliza_segun_la_prioridad():
    d, ctx = datos_y_contexto([PEDIDO_A, PEDIDO_B])
    it = simular_ruta([1, 0], ctx, d)  # B primero: A se atiende después de las 09:00
    assert it.paradas[1].retraso_s > 0
    assert it.retraso_ponderado_min == pytest.approx(it.paradas[1].retraso_s / 60)  # ESTANDAR pesa 1

    d2, ctx2 = datos_y_contexto([Pedido("A", 20.0, "EXPRESS", hora(8), hora(9)), PEDIDO_B])
    it2 = simular_ruta([1, 0], ctx2, d2)
    assert it2.retraso_ponderado_min == pytest.approx(5 * it2.paradas[1].retraso_s / 60)  # EXPRESS pesa 5


def test_el_costo_combina_distancia_combustible_co2_y_retraso():
    d, ctx = datos_y_contexto([PEDIDO_A, PEDIDO_B])
    it = simular_ruta([1, 0], ctx, d)
    km = it.distancia_m / 1000
    esperado = km * (1.0 + 1.0 / 10.0 + 2.0 * 0.25) + 0.5 * it.retraso_ponderado_min
    assert it.costo == pytest.approx(esperado)
    assert it.litros == pytest.approx(km / 10.0) and it.co2_kg == pytest.approx(km * 0.25)


def test_descanso_de_una_hora_tras_cuatro_horas_de_trabajo_continuo():
    largas = np.array([[0, 10800, 10800], [10800, 0, 10800], [10800, 10800, 0]], dtype=float)  # tramos de 3 h
    conductor = Conductor("C1", "A-IIb", FECHA + timedelta(days=100), hora(6), hora(23))
    problema = Problema(
        [Pedido("A", 1, "ESTANDAR", hora(8), hora(23)), Pedido("B", 1, "ESTANDAR", hora(8), hora(23))],
        [VEHICULO], [conductor], largas * 10, largas, Parametros(fecha=FECHA, jornada_max_s=14 * 3600),
    )
    d, ctx = Datos(problema), ContextoPar.crear(Par(VEHICULO, conductor), problema.parametros)
    it = simular_ruta([0, 1], ctx, d)
    assert it.descansos >= 1
    # 3 h de viaje + 10 min de atención + 3 h = 6 h 10 min > 4 h: el descanso va antes del segundo tramo
    assert it.paradas[1].llegada_s == hora(8) + 10800 + 600 + 3600 + 10800


def test_la_ruta_es_invalida_si_supera_la_jornada_del_conductor():
    corto = Conductor("C1", "A-IIb", FECHA + timedelta(days=100), hora(6), hora(9))
    d, ctx = datos_y_contexto([PEDIDO_A, PEDIDO_B], conductor=corto)
    it = simular_ruta([0, 1], ctx, d)
    assert not it.valida and it.motivo_invalida == "JORNADA"


def test_la_ruta_es_invalida_si_supera_la_capacidad():
    chico = Vehiculo("V1", "ABC-101", "CAMIONETA", 40.0, 10.0, 0.25)
    d, ctx = datos_y_contexto([PEDIDO_A, PEDIDO_B], vehiculo=chico)  # 20 + 30 kg > 40 kg
    it = simular_ruta([0, 1], ctx, d)
    assert not it.valida and it.motivo_invalida == "CAPACIDAD"


def test_un_express_despues_de_un_estandar_invalida_la_ruta():
    express = Pedido("B", 30.0, "EXPRESS", hora(9), hora(10))
    d, ctx = datos_y_contexto([PEDIDO_A, express])
    assert simular_ruta([1, 0], ctx, d).valida
    malo = simular_ruta([0, 1], ctx, d)
    assert not malo.valida and malo.motivo_invalida == "ORDEN_EXPRESS"


def test_una_ruta_vacia_no_tiene_distancia_ni_costo():
    d, ctx = datos_y_contexto([PEDIDO_A])
    it = simular_ruta([], ctx, d)
    assert it.distancia_m == 0 and it.costo == 0 and it.valida


# --------------------------------------------------------------------------------------------- 4.2 elegibilidad
def conductor(id_, categoria="A-IIb", dias=100, inicio=6, fin=14, disponible=True):
    return Conductor(id_, categoria, FECHA + timedelta(days=dias), hora(inicio), hora(fin), disponible)


def vehiculo(id_, tipo="CAMIONETA", placa="ABC-101", capacidad=1000.0, factor=0.25, estado="DISPONIBLE"):
    return Vehiculo(id_, placa, tipo, capacidad, 10.0, factor, estado)


def test_las_categorias_de_licencia_son_compatibles_con_su_familia_de_vehiculos():
    assert licencia_compatible("CAMIONETA", "A-IIb") and licencia_compatible("FURGON", "A-I")
    assert licencia_compatible("MOTO", "B-IIa") and licencia_compatible("MOTO", "B-IIb")
    assert not licencia_compatible("FURGON", "B-IIa") and not licencia_compatible("MOTO", "A-IIb")


def test_un_conductor_con_la_licencia_vencida_no_se_asigna():
    p = Parametros(fecha=FECHA)
    emp = emparejar([vehiculo("V1")], [conductor("C1", dias=-1), conductor("C2", dias=0)], p)
    assert emp.pares == []  # vencida ayer y vence hoy: ninguna sirve para la jornada de hoy
    assert emparejar([vehiculo("V1")], [conductor("C3", dias=1)], p).pares  # vence mañana: sirve


def test_un_conductor_de_moto_no_maneja_una_furgoneta():
    p = Parametros(fecha=FECHA)
    assert emparejar([vehiculo("V1", tipo="FURGON")], [conductor("C1", "B-IIa")], p).pares == []
    assert emparejar([vehiculo("V1", tipo="MOTO")], [conductor("C1", "B-IIa")], p).pares


def test_vehiculos_no_disponibles_y_conductores_no_disponibles_se_excluyen():
    p = Parametros(fecha=FECHA)
    emp = emparejar(
        [vehiculo("V1", estado="MANTENIMIENTO"), vehiculo("V2", estado="EN_RUTA")],
        [conductor("C1", disponible=False)],
        p,
    )
    assert emp.pares == [] and emp.vehiculos_elegibles == 0 and emp.conductores_elegibles == 0


def test_sin_tabla_de_restriccion_por_placa_ningun_vehiculo_se_excluye():
    p = Parametros(fecha=FECHA)  # FECHA es lunes
    assert emparejar([vehiculo("V1", placa="ABC-103")], [conductor("C1")], p).pares


def test_con_tabla_de_restriccion_el_vehiculo_restringido_ese_dia_no_recibe_ruta():
    v, c = vehiculo("V1", placa="ABC-103"), conductor("C1")
    lunes_restringido = Parametros(fecha=FECHA, restriccion_placa={3: {0}})  # placas terminadas en 3, lunes
    emp = emparejar([v], [c], lunes_restringido)
    assert emp.pares == [] and emp.vehiculos_restringidos == ["ABC-103"]
    martes = Parametros(fecha=FECHA + timedelta(days=1), restriccion_placa={3: {0}})
    assert emparejar([v], [c], martes).pares


def test_los_pares_se_ordenan_del_vehiculo_mas_eficiente_al_menos_eficiente():
    p = Parametros(fecha=FECHA)
    vs = [vehiculo("V1", placa="A-1", factor=0.40), vehiculo("V2", placa="A-2", factor=0.20)]
    emp = emparejar(vs, [conductor("C1"), conductor("C2")], p)
    assert [par.vehiculo.id for par in emp.pares] == ["V2", "V1"]


def test_el_vehiculo_mas_grande_recibe_al_conductor_con_la_disponibilidad_mas_amplia():
    p = Parametros(fecha=FECHA)
    emp = emparejar(
        [vehiculo("chico", capacidad=500), vehiculo("grande", capacidad=2000)],
        [conductor("corto", inicio=8, fin=12), conductor("largo", inicio=6, fin=14)],
        p,
    )
    asignados = {par.vehiculo.id: par.conductor.id for par in emp.pares}
    assert asignados == {"grande": "largo", "chico": "corto"}


# --------------------------------------------------------------------------------------------- 4.3 solución voraz
def test_la_solucion_voraz_cubre_cada_pedido_una_sola_vez_y_respeta_la_capacidad():
    problema = problema_aleatorio(40, 4, semilla=2)
    d = Datos(problema)
    pares = emparejar(problema.vehiculos, problema.conductores, problema.parametros).pares
    contextos = [ContextoPar.crear(par, problema.parametros) for par in pares]
    sol = solucion_voraz(d, contextos)
    vistos = [c for _, secuencia in sol.rutas for c in secuencia] + sol.sin_asignar
    assert sorted(vistos) == list(range(40))
    for (k, secuencia), it in zip(sol.rutas, sol.itinerarios):
        assert it.valida
        assert sum(d.peso_l[c] for c in secuencia) <= contextos[k].capacidad_kg + 1e-9


def test_en_cada_ruta_los_express_van_primero():
    problema = problema_aleatorio(40, 4, semilla=5, pct_express=0.3)
    d = Datos(problema)
    pares = emparejar(problema.vehiculos, problema.conductores, problema.parametros).pares
    contextos = [ContextoPar.crear(par, problema.parametros) for par in pares]
    sol = solucion_voraz(d, contextos)
    assert d.express.any()
    for _, secuencia in sol.rutas:
        marcas = [d.express_l[c] for c in secuencia]
        assert marcas == sorted(marcas, reverse=True)  # primero todos los express, luego los demás


def test_un_pedido_pesado_y_otro_liviano_van_en_vehiculos_distintos_si_no_caben_juntos():
    problema = problema_aleatorio(2, 2, semilla=1, capacidad=(100.0, 100.0))
    problema.pedidos[0] = Pedido("P0", 80.0, "ESTANDAR", hora(8), hora(18))
    problema.pedidos[1] = Pedido("P1", 80.0, "ESTANDAR", hora(8), hora(18))
    r = resolver(problema)
    assert len(r.rutas) == 2 and not r.sin_cobertura


# --------------------------------------------------------------------------------------------- 4.4 ACO
def test_el_aco_nunca_es_peor_que_la_solucion_voraz_inicial():
    for semilla in (1, 2, 3):
        r = resolver(problema_aleatorio(30, 4, semilla=semilla, tiempo_max_s=None, max_iteraciones=15))
        assert r.costo <= r.costo_base + 1e-9
        assert all(x.itinerario.valida for x in r.rutas)


def test_el_aco_mejora_a_la_solucion_voraz_en_un_caso_con_margen():
    r = resolver(problema_aleatorio(60, 6, semilla=4, tiempo_max_s=None, max_iteraciones=25))
    assert r.costo < r.costo_base


def test_con_la_misma_semilla_y_las_mismas_iteraciones_el_resultado_es_identico():
    def ejecutar():
        r = resolver(problema_aleatorio(25, 3, semilla=6, tiempo_max_s=None, max_iteraciones=10))
        return [[p.pedido_id for p in x.itinerario.paradas] for x in r.rutas], r.costo

    assert ejecutar() == ejecutar()


def test_la_busqueda_respeta_el_presupuesto_de_tiempo():
    problema = problema_aleatorio(80, 8, semilla=7, tiempo_max_s=2.0)
    inicio = time.perf_counter()
    r = resolver(problema)
    duracion = time.perf_counter() - inicio
    assert duracion < 3.5  # presupuesto de 2 s más la tolerancia de un paso de construcción
    assert r.tiempo_s == pytest.approx(duracion, abs=0.2)
    assert r.costo <= r.costo_base + 1e-9


def test_todas_las_rutas_devueltas_son_validas_y_cada_pedido_aparece_una_sola_vez():
    for semilla in (11, 12):
        problema = problema_aleatorio(35, 4, semilla=semilla, tiempo_max_s=None, max_iteraciones=8, pct_express=0.2)
        r = resolver(problema)
        ids = [p.pedido_id for x in r.rutas for p in x.itinerario.paradas] + [s.pedido_id for s in r.sin_cobertura]
        assert sorted(ids) == sorted(x.id for x in problema.pedidos)
        for x in r.rutas:
            assert x.itinerario.valida
            assert sum(next(q.peso_kg for q in problema.pedidos if q.id == p.pedido_id) for p in x.itinerario.paradas) <= x.par.vehiculo.capacidad_kg + 1e-9


def test_el_motor_prefiere_el_vehiculo_de_menor_emision():
    problema = problema_aleatorio(1, 2, semilla=1, capacidad=(500.0, 500.0))
    problema.vehiculos[0] = Vehiculo("sucio", "ABC-1", "CAMIONETA", 500.0, 10.0, 0.40)
    problema.vehiculos[1] = Vehiculo("limpio", "ABC-2", "CAMIONETA", 500.0, 10.0, 0.15)
    r = resolver(problema)
    assert [x.par.vehiculo.id for x in r.rutas] == ["limpio"]


# --------------------------------------------------------------------------------------------- 4.5 sin cobertura
def test_un_pedido_mas_pesado_que_toda_la_flota_queda_sin_cobertura_por_capacidad():
    problema = problema_aleatorio(5, 2, semilla=1, capacidad=(300.0, 300.0))
    problema.pedidos[2] = Pedido("PESADO", 5000.0, "ESTANDAR", hora(8), hora(18))
    r = resolver(problema)
    sin = {s.pedido_id: s for s in r.sin_cobertura}
    assert sin["PESADO"].motivo == PESO_EXCEDE_CAPACIDAD
    assert "Divida" in sin["PESADO"].sugerencia
    assert len(r.rutas) >= 1 and not r.imposible


def test_sin_vehiculos_o_conductores_elegibles_no_hay_rutas_y_todos_quedan_sin_cobertura():
    problema = problema_aleatorio(6, 3, semilla=1)
    problema.conductores = []
    r = resolver(problema)
    assert r.imposible and r.rutas == []
    assert len(r.sin_cobertura) == 6 and {s.motivo for s in r.sin_cobertura} == {SIN_RECURSOS}
    assert "no es posible" in r.mensaje.lower()


def test_un_pedido_cuya_ventana_queda_fuera_de_la_jornada_se_informa():
    problema = problema_aleatorio(4, 2, semilla=1)
    problema.pedidos[1] = Pedido("TARDE", 10.0, "ESTANDAR", hora(18), hora(20))  # abre cuando ya terminó el conductor
    r = resolver(problema)
    sin = {s.pedido_id: s for s in r.sin_cobertura}
    assert sin["TARDE"].motivo == FUERA_DE_JORNADA


def test_si_la_flota_no_alcanza_los_pedidos_sobrantes_se_marcan_como_flota_insuficiente():
    problema = problema_aleatorio(12, 1, semilla=1, capacidad=(200.0, 200.0), peso_max=100.0)
    for i in range(12):
        problema.pedidos[i] = Pedido(f"P{i:03d}", 90.0, "ESTANDAR", hora(8), hora(18))
    r = resolver(problema)
    assert r.sin_cobertura and {s.motivo for s in r.sin_cobertura} == {FLOTA_INSUFICIENTE}
    assert len(r.rutas) == 1 and sum(len(x.itinerario.paradas) for x in r.rutas) == 2  # 2 × 90 kg ≤ 200 kg


def test_sin_pedidos_el_resultado_esta_vacio():
    problema = problema_aleatorio(3, 2, semilla=1)
    problema.pedidos = []
    problema.distancia_m = problema.distancia_m[:1, :1]
    problema.tiempo_s = problema.tiempo_s[:1, :1]
    r = resolver(problema)
    assert r.rutas == [] and r.sin_cobertura == [] and not r.imposible
