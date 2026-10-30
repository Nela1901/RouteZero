"""Datos derivados, simulación de itinerarios y función objetivo.

`simular_ruta` es la referencia exacta de cómo se calcula una ruta (espera, atención, descansos, jornada y
costo). Las búsquedas (voraz, ACO, mejora local) la usan para comprobar cada solución, y la construcción
vectorizada de `construccion.py` replica sus reglas paso a paso.
"""

from dataclasses import dataclass

import numpy as np

from src.algoritmo.modelo import Arranque, Itinerario, Par, Parada, Parametros, Problema

EPS = 1e-9


class Datos:
    """Arreglos de numpy y listas de Python derivados de un `Problema`, calculados una sola vez."""

    def __init__(self, problema: Problema):
        self.p: Parametros = problema.parametros
        self.pedidos = problema.pedidos
        self.n = len(problema.pedidos)
        self.T = np.asarray(problema.tiempo_s, dtype=np.float64)
        self.D = np.asarray(problema.distancia_m, dtype=np.float64)
        self.tiempo_lista = self.T.tolist()   # listas de Python: más rápidas que numpy para acceso escalar
        # Tiempos por franja horaria (HU-012/HU-013, RF-003): un tramo usa la matriz de hora punta si sale en una franja
        self.franjas = tuple(self.p.franjas_punta)
        self.hay_punta = problema.tiempo_punta_s is not None and len(self.franjas) > 0
        self.tiempo_punta = np.asarray(problema.tiempo_punta_s, dtype=np.float64) if self.hay_punta else self.T
        self.tiempo_punta_lista = self.tiempo_punta.tolist() if self.hay_punta else self.tiempo_lista
        self.distancia_lista = self.D.tolist()
        self.peso = np.array([x.peso_kg for x in problema.pedidos], dtype=np.float64)
        self.w_ini = np.array([x.ventana_inicio_s for x in problema.pedidos], dtype=np.float64)
        self.w_fin = np.array([x.ventana_fin_s for x in problema.pedidos], dtype=np.float64)
        self.pond = np.array([self.p.ponderacion_prioridad[x.prioridad] for x in problema.pedidos], dtype=np.float64)
        self.express = np.array([x.prioridad == "EXPRESS" for x in problema.pedidos], dtype=bool)
        self.peso_l = self.peso.tolist()
        self.w_ini_l = self.w_ini.tolist()
        self.w_fin_l = self.w_fin.tolist()
        self.pond_l = self.pond.tolist()
        self.express_l = self.express.tolist()

    def en_punta(self, t: float) -> bool:
        for inicio, fin in self.franjas:
            if inicio <= t < fin:
                return True
        return False

    def en_punta_arr(self, t: np.ndarray) -> np.ndarray:
        dentro = np.zeros(t.shape, dtype=bool)
        for inicio, fin in self.franjas:
            dentro |= (t >= inicio) & (t < fin)
        return dentro

    def tl_en(self, t: float) -> list:
        """Tiempos (listas de Python) de los tramos que salen en el instante `t`."""
        return self.tiempo_punta_lista if self.hay_punta and self.en_punta(t) else self.tiempo_lista

    def t_en(self, t: float) -> np.ndarray:
        """Tiempos (numpy) de los tramos que salen en el instante `t`."""
        return self.tiempo_punta if self.hay_punta and self.en_punta(t) else self.T

    def vuelta_en(self, t: np.ndarray, idx1: np.ndarray) -> np.ndarray:
        """Tiempo de volver al depósito desde cada candidato, según la hora a la que sale cada uno."""
        if not self.hay_punta:
            return self.T[idx1, 0]
        return np.where(self.en_punta_arr(t), self.tiempo_punta[idx1, 0], self.T[idx1, 0])


@dataclass
class ContextoPar:
    """Constantes de un par vehículo-conductor para una jornada."""

    par: Par
    salida_s: float
    limite_s: float
    capacidad_kg: float
    consumo_km_l: float
    factor_co2: float
    costo_por_km: float  # costo de distancia + combustible + CO2 por kilómetro recorrido
    nodo_inicio: int = 0            # índice de la matriz de donde parte (0 = depósito)
    trabajo_inicial_s: float = 0.0  # trabajo continuo ya acumulado al partir

    @classmethod
    def crear(cls, par: Par, p: Parametros, arranque: Arranque | None = None) -> "ContextoPar":
        salida = max(float(p.hora_inicio_jornada_s), float(par.conductor.inicio_s))
        limite = min(salida + p.jornada_max_s, float(par.conductor.fin_s))  # la jornada cuenta desde la salida original
        v = par.vehiculo
        por_km = p.peso_distancia + p.peso_combustible / v.consumo_km_l + p.peso_co2 * v.factor_co2_kg_km
        if arranque is None:
            return cls(par, salida, limite, v.capacidad_kg, v.consumo_km_l, v.factor_co2_kg_km, por_km)
        return cls(
            par, max(salida, float(arranque.salida_s)), limite, v.capacidad_kg, v.consumo_km_l, v.factor_co2_kg_km, por_km,
            arranque.nodo, float(arranque.trabajo_s),
        )


def simular_ruta(secuencia: list, ctx: ContextoPar, d: Datos) -> Itinerario:
    """Itinerario de una ruta que visita los pedidos de `secuencia` (índices de pedido) en ese orden."""
    p = d.p
    t = ctx.salida_s
    trabajo = ctx.trabajo_inicial_s
    pos = ctx.nodo_inicio
    metros = 0.0
    carga = 0.0
    descansos = 0
    retraso_pond_min = 0.0
    paradas = []
    express_visto_despues = False
    no_express_visto = False

    for orden, c in enumerate(secuencia, start=1):
        if d.express_l[c]:
            express_visto_despues = express_visto_despues or no_express_visto
        else:
            no_express_visto = True
        viaje = d.tl_en(t)[pos][c + 1]
        if trabajo + viaje > p.descanso_cada_s:
            t += p.descanso_s
            trabajo = 0.0
            descansos += 1
            viaje = d.tl_en(t)[pos][c + 1]  # tras el descanso el tramo sale más tarde: puede cambiar de franja
        t += viaje
        trabajo += viaje
        metros += d.distancia_lista[pos][c + 1]
        llegada = t
        inicio = max(llegada, d.w_ini_l[c])
        retraso = max(0.0, inicio - d.w_fin_l[c])
        t = inicio + p.atencion_s
        trabajo += p.atencion_s
        carga += d.peso_l[c]
        retraso_pond_min += d.pond_l[c] * retraso / 60.0
        paradas.append(Parada(d.pedidos[c].id, orden, llegada, inicio, retraso))
        pos = c + 1

    vuelta = d.tl_en(t)[pos][0]
    if secuencia and trabajo + vuelta > p.descanso_cada_s:
        t += p.descanso_s
        descansos += 1
        vuelta = d.tl_en(t)[pos][0]
    t += vuelta
    metros += d.distancia_lista[pos][0]
    if not secuencia:
        t, metros = ctx.salida_s, 0.0

    km = metros / 1000.0
    litros = km / ctx.consumo_km_l
    co2 = km * ctx.factor_co2
    costo = km * ctx.costo_por_km + p.peso_retraso * retraso_pond_min

    motivo = ""
    if t > ctx.limite_s + EPS:
        motivo = "JORNADA"
    elif carga > ctx.capacidad_kg + EPS:
        motivo = "CAPACIDAD"
    elif express_visto_despues:
        motivo = "ORDEN_EXPRESS"
    return Itinerario(
        salida_s=ctx.salida_s,
        regreso_s=t,
        distancia_m=metros,
        litros=litros,
        co2_kg=co2,
        retraso_ponderado_min=retraso_pond_min,
        costo=costo,
        descansos=descansos,
        paradas=paradas,
        valida=motivo == "",
        motivo_invalida=motivo,
    )


def costo_de_solucion(costos_rutas: list, sin_asignar: list, d: Datos) -> float:
    """Costo total: rutas más una penalización fuerte por cada pedido sin asignar (ponderada por prioridad)."""
    penal = sum(d.p.penalizacion_sin_cobertura * d.pond_l[c] for c in sin_asignar)
    return float(sum(costos_rutas)) + penal
