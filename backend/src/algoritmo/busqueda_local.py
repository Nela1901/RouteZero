"""Mejora local de una solución: inserción de pedidos sin asignar, 2-opt dentro de cada ruta y reubicación
de paradas entre rutas.

Cada movimiento se comprueba con `simular_ruta`, así que las restricciones (capacidad, jornada, descansos y
orden express) se respetan siempre. La búsqueda es de primera mejora y se detiene al agotar el número de
evaluaciones o el tiempo disponible.
"""

import time

from src.algoritmo.construccion import Solucion, evaluar_solucion
from src.algoritmo.evaluacion import Datos, simular_ruta

TOLERANCIA = 1e-9


def mejorar(sol: Solucion, d: Datos, contextos: list, rng, limite_t: float | None = None, max_evaluaciones: int = 2000) -> Solucion:
    rutas = [[k, list(secuencia)] for k, secuencia in sol.rutas]
    sin = list(sol.sin_asignar)
    cache: dict = {}
    evaluaciones = 0

    def evaluar(k: int, secuencia: list) -> tuple:
        nonlocal evaluaciones
        if not secuencia:
            return 0.0, True
        clave = (k, tuple(secuencia))
        resultado = cache.get(clave)
        if resultado is None:
            evaluaciones += 1
            itinerario = simular_ruta(secuencia, contextos[k], d)
            resultado = cache[clave] = (itinerario.costo, itinerario.valida)
        return resultado

    def agotado() -> bool:
        return evaluaciones >= max_evaluaciones or (limite_t is not None and time.perf_counter() >= limite_t)

    costos = [evaluar(k, s)[0] for k, s in rutas]

    def insertar_sin_asignar() -> bool:
        mejoro = False
        for u in list(sin):
            penalizacion = d.p.penalizacion_sin_cobertura * d.pond_l[u]
            mejor = None  # (delta, indice de ruta, posición) o (delta, None, vehículo sin usar)
            for ri, (k, secuencia) in enumerate(rutas):
                for pos in range(len(secuencia) + 1):
                    costo, valida = evaluar(k, secuencia[:pos] + [u] + secuencia[pos:])
                    if valida and (mejor is None or costo - costos[ri] < mejor[0]):
                        mejor = (costo - costos[ri], ri, pos)
                if agotado():
                    return mejoro
            usados = {k for k, _ in rutas}
            for k in range(len(contextos)):
                if k not in usados:
                    costo, valida = evaluar(k, [u])
                    if valida and (mejor is None or costo < mejor[0]):
                        mejor = (costo, None, k)
            if mejor is not None and mejor[0] < penalizacion:
                delta, ri, donde = mejor
                if ri is None:
                    rutas.append([donde, [u]])
                    costos.append(evaluar(donde, [u])[0])
                else:
                    rutas[ri][1].insert(donde, u)
                    costos[ri] = evaluar(rutas[ri][0], rutas[ri][1])[0]
                sin.remove(u)
                mejoro = True
        return mejoro

    def dos_opt() -> bool:
        mejoro = False
        for ri, (k, secuencia) in enumerate(rutas):
            for i in range(len(secuencia) - 1):
                for j in range(i + 1, len(secuencia)):
                    nueva = secuencia[:i] + secuencia[i : j + 1][::-1] + secuencia[j + 1 :]
                    costo, valida = evaluar(k, nueva)
                    if valida and costo < costos[ri] - TOLERANCIA:
                        rutas[ri][1] = secuencia = nueva
                        costos[ri] = costo
                        mejoro = True
                if agotado():
                    return mejoro
        return mejoro

    def reubicar() -> bool:
        mejoro = False
        asignados = [c for _, secuencia in rutas for c in secuencia]
        for c in [asignados[i] for i in rng.permutation(len(asignados))]:
            origen = next((ri for ri, (_, s) in enumerate(rutas) if c in s), None)
            if origen is None:
                continue
            k_o, seq_o = rutas[origen]
            sin_c = [x for x in seq_o if x != c]
            costo_sin, valida_sin = evaluar(k_o, sin_c)
            if not valida_sin:
                continue
            ahorro = costos[origen] - costo_sin
            mejor = None
            for rj, (k_j, seq_j) in enumerate(rutas):
                base = sin_c if rj == origen else seq_j
                costo_base = costo_sin if rj == origen else costos[rj]
                for pos in range(len(base) + 1):
                    if rj == origen and seq_o == base[:pos] + [c] + base[pos:]:
                        continue
                    costo_nuevo, valida = evaluar(k_j, base[:pos] + [c] + base[pos:])
                    if not valida:
                        continue
                    delta = (costo_nuevo - costo_base) - (0.0 if rj == origen else ahorro)
                    if rj == origen:
                        delta = costo_nuevo - costos[origen]
                    if mejor is None or delta < mejor[0]:
                        mejor = (delta, rj, pos)
                if agotado():
                    return mejoro
            if mejor is not None and mejor[0] < -TOLERANCIA:
                _, rj, pos = mejor
                if rj == origen:
                    rutas[origen][1] = sin_c[:pos] + [c] + sin_c[pos:]
                else:
                    rutas[origen][1] = sin_c
                    rutas[rj][1] = rutas[rj][1][:pos] + [c] + rutas[rj][1][pos:]
                for ri in {origen, rj}:
                    costos[ri] = evaluar(rutas[ri][0], rutas[ri][1])[0]
                mejoro = True
        return mejoro

    while not agotado():
        algo = insertar_sin_asignar()
        algo = dos_opt() or algo
        algo = reubicar() or algo
        if not algo:
            break
        # Las rutas que quedaron vacías liberan su vehículo
        vivos = [i for i, (_, s) in enumerate(rutas) if s]
        rutas = [rutas[i] for i in vivos]
        costos = [costos[i] for i in vivos]

    return evaluar_solucion(d, contextos, [(k, s) for k, s in rutas if s], sin)
