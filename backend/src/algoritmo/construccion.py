"""Construcción de soluciones: solución inicial voraz y paso de construcción de una hormiga del ACO.

Ambas comparten el mismo procedimiento vectorizado con numpy: para cada vehículo se arma una ruta
agregando, paso a paso, el siguiente pedido entre los que todavía caben (capacidad, jornada del
conductor, descansos). Sin feromonas (`tau=None`) se elige siempre el mejor candidato (voraz); con
feromonas se aplica la regla pseudoaleatoria proporcional del ACS.

Regla express (RN-008): mientras quede algún pedido EXPRESS que todavía quepa en la ruta, solo se
consideran pedidos EXPRESS; así, dentro de cada ruta los EXPRESS van primero.
"""

from dataclasses import dataclass, field

import numpy as np

from src.algoritmo.evaluacion import EPS, ContextoPar, Datos, costo_de_solucion, simular_ruta
from src.algoritmo.modelo import Itinerario


@dataclass
class Solucion:
    rutas: list                      # [(indice del par, [índices de pedido en orden])]
    sin_asignar: list                # índices de pedido que no entraron en ninguna ruta
    itinerarios: list = field(default_factory=list)
    costo: float = 0.0

    def arcos(self) -> list:
        """Pares (desde, hacia) en índices de matriz, incluidos los viajes desde y hacia el depósito."""
        salida = []
        for _, secuencia in self.rutas:
            anterior = 0
            for c in secuencia:
                salida.append((anterior, c + 1))
                anterior = c + 1
            salida.append((anterior, 0))
        return salida


def construir(d: Datos, contextos: list, tau, rng, q0: float = 1.0, alfa: float = 1.0, beta: float = 3.0):
    """Arma rutas para los vehículos de `contextos`, en ese orden. Devuelve (rutas, sin_asignar)."""
    p = d.p
    libres = np.ones(d.n, dtype=bool)
    rutas = []
    for k, ctx in enumerate(contextos):
        if not libres.any():
            break
        secuencia: list[int] = []
        t, trabajo, pos, carga = ctx.salida_s, 0.0, 0, 0.0
        while True:
            idx = np.flatnonzero(libres)
            if idx.size == 0:
                break
            idx1 = idx + 1
            viaje = d.T[pos, idx1]
            necesita = (trabajo + viaje) > p.descanso_cada_s
            llegada = t + necesita * p.descanso_s + viaje
            inicio = np.maximum(llegada, d.w_ini[idx])
            retraso = np.maximum(0.0, inicio - d.w_fin[idx])
            fin = inicio + p.atencion_s
            trabajo_f = np.where(necesita, 0.0, trabajo) + viaje + p.atencion_s
            vuelta = d.T[idx1, 0]
            necesita_vuelta = (trabajo_f + vuelta) > p.descanso_cada_s
            t_fin = fin + necesita_vuelta * p.descanso_s + vuelta
            cabe = (t_fin <= ctx.limite_s + EPS) & (carga + d.peso[idx] <= ctx.capacidad_kg + EPS)
            if not cabe.any():
                break
            es_express = d.express[idx]
            if (cabe & es_express).any():
                cabe &= es_express
            sel = np.flatnonzero(cabe)

            km = d.D[pos, idx1[sel]] / 1000.0
            costo_inc = km * ctx.costo_por_km + p.peso_retraso * d.pond[idx[sel]] * retraso[sel] / 60.0
            holgura_h = np.maximum(0.0, d.w_fin[idx[sel]] - inicio[sel]) / 3600.0
            eta = 1.0 / (costo_inc + 0.5 * holgura_h + 0.01)
            if tau is None:
                j = int(np.argmax(eta))
            else:
                pesos = (tau[pos, idx1[sel]] ** alfa) * (eta ** beta)
                if rng.random() < q0:
                    j = int(np.argmax(pesos))
                else:
                    acumulado = np.cumsum(pesos)
                    j = min(int(np.searchsorted(acumulado, rng.random() * acumulado[-1])), len(pesos) - 1)

            s = sel[j]
            c = int(idx[s])
            secuencia.append(c)
            libres[c] = False
            t, trabajo, pos, carga = float(fin[s]), float(trabajo_f[s]), c + 1, carga + d.peso_l[c]
        if secuencia:
            rutas.append((k, secuencia))
    return rutas, [int(i) for i in np.flatnonzero(libres)]


def evaluar_solucion(d: Datos, contextos: list, rutas: list, sin_asignar: list) -> Solucion:
    """Simula cada ruta y calcula el costo total. Una ruta inválida (no debería ocurrir) se descarta y sus
    pedidos pasan a sin asignar, para que la solución devuelta sea siempre válida."""
    validas, itinerarios, costos, sin = [], [], [], list(sin_asignar)
    for k, secuencia in rutas:
        itinerario: Itinerario = simular_ruta(secuencia, contextos[k], d)
        if itinerario.valida:
            validas.append((k, secuencia))
            itinerarios.append(itinerario)
            costos.append(itinerario.costo)
        else:
            sin.extend(secuencia)
    return Solucion(validas, sorted(sin), itinerarios, costo_de_solucion(costos, sin, d))


def solucion_voraz(d: Datos, contextos: list) -> Solucion:
    rutas, sin = construir(d, contextos, None, None)
    return evaluar_solucion(d, contextos, rutas, sin)
