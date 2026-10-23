"""Congestión de las vías de la RN-012: franjas de hora punta (RF-003), factores de lentitud y nivel para el mapa.

Supuestos pendientes de calibrar (no hay datos reales de tráfico de Huancayo): las franjas salen de RF-003 y los
factores de hora punta son una estimación razonable; se ajustan en `FACTOR_PUNTA`.
"""

# Las tres vías de la RN-012, tal como se guardan en `incidentes_trafico`
FERROCARRIL, GIRALDEZ, CALLE_REAL = "Av. Ferrocarril", "Av. Giráldez", "Calle Real"
VIAS = (FERROCARRIL, GIRALDEZ, CALLE_REAL)
# Cómo se busca cada una en el grafo (sin tildes ni mayúsculas)
CLAVE_EN_GRAFO = {FERROCARRIL: "ferrocarril", GIRALDEZ: "giraldez", CALLE_REAL: "calle real"}

# RF-003: 7:30-9:30, 12:00-14:30 y 17:00-21:00 (segundos desde la medianoche)
FRANJAS_PUNTA = ((7 * 3600 + 1800, 9 * 3600 + 1800), (12 * 3600, 14 * 3600 + 1800), (17 * 3600, 21 * 3600))
# Cuántas veces más lento se circula por cada vía en hora punta
FACTOR_PUNTA = {FERROCARRIL: 1.8, GIRALDEZ: 1.6, CALLE_REAL: 1.3}

UMBRAL_ROJO = 2.0   # desde 2 veces más lento el nivel es rojo
EPSILON = 1e-9


def en_punta(segundos: float) -> bool:
    return any(inicio <= segundos < fin for inicio, fin in FRANJAS_PUNTA)


def factores_de_incidentes(incidentes: list[dict]) -> dict[str, float]:
    """Factor vigente por vía: el mayor de los incidentes activos sobre ella."""
    factores: dict[str, float] = {}
    for i in incidentes:
        if i["calle"] in CLAVE_EN_GRAFO:
            factores[i["calle"]] = max(factores.get(i["calle"], 1.0), float(i["factor"]))
    return factores


def factores_en_grafo(factores_por_via: dict[str, float]) -> dict[str, float] | None:
    """Pasa {vía: factor} a {clave en el grafo: factor}; None si no hay nada que encarecer."""
    salida = {CLAVE_EN_GRAFO[v]: f for v, f in factores_por_via.items() if f > 1.0 + EPSILON}
    return salida or None


def factores_de_matrices(incidentes: list[dict]) -> tuple[dict[str, float] | None, dict[str, float] | None]:
    """(factores para la matriz normal, factores para la matriz de hora punta), en claves del grafo.

    La normal solo lleva los incidentes; la de punta lleva además el factor de hora punta de cada vía (un incidente
    en hora punta empeora aún más el tránsito, por eso se multiplican)."""
    inc = factores_de_incidentes(incidentes)
    punta = {v: FACTOR_PUNTA[v] * inc.get(v, 1.0) for v in VIAS}
    return factores_en_grafo(inc), factores_en_grafo(punta)


def factores_de_la_hora(incidentes: list[dict], segundos: float) -> dict[str, float] | None:
    """Factores (claves del grafo) que rigen para un tramo que sale a esa hora."""
    normal, punta = factores_de_matrices(incidentes)
    return punta if en_punta(segundos) else normal


def factor_efectivo(via: str, segundos: float, incidentes: list[dict]) -> tuple[float, list[str]]:
    """Cuántas veces más lenta está la vía a esa hora y por qué (hora punta, incidente o ambos)."""
    inc = factores_de_incidentes(incidentes).get(via, 1.0)
    punta = FACTOR_PUNTA[via] if en_punta(segundos) else 1.0
    motivos = []
    if punta > 1.0:
        motivos.append("hora punta")
    if inc > 1.0:
        motivos.append("incidente")
    return punta * inc, motivos


def nivel(factor: float) -> str:
    if factor <= 1.0 + EPSILON:
        return "VERDE"
    return "AMARILLO" if factor < UMBRAL_ROJO else "ROJO"


def firma(incidentes: list[dict]) -> tuple:
    """Identifica el conjunto de incidentes vigentes (para la caché de trazados)."""
    return tuple(sorted(factores_de_incidentes(incidentes).items()))

