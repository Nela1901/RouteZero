"""Genera el grafo de calles de Huancayo que usa el motor de rutas (cambio `add-motor-rutas`).

Descarga de OpenStreetMap (API Overpass) las vías por las que circulan vehículos en la zona urbana de
Huancayo, arma un grafo dirigido (respetando sentidos únicos y rotondas), conserva solo la mayor
componente fuertemente conexa y lo guarda en `backend/data/huancayo_grafo.npz`.

Se ejecuta una sola vez (o cuando se quiera refrescar el mapa); en ejecución el backend solo lee el
archivo y no llama a ningún servicio externo.

Uso (desde `backend/`):
    python scripts/generar_grafo.py                       # descarga y genera el archivo
    python scripts/generar_grafo.py --entrada osm.json    # reconstruye desde una descarga guardada
    python scripts/generar_grafo.py --guardar-descarga osm.json

Datos © OpenStreetMap contributors (licencia ODbL).
"""

import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

# Zona urbana de Huancayo, Chilca y El Tambo: sur, oeste, norte, este.
CAJA = (-12.12, -75.27, -11.99, -75.17)

ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)

# Velocidad base (km/h) por tipo de vía, alineada con el DS 033-2001-MTC art. 162:
# calles y jirones 40, avenidas 60, vías expresas 80. Las residenciales y de servicio se limitan más.
VELOCIDAD_KMH = {
    "motorway": 80, "motorway_link": 60, "trunk": 60, "trunk_link": 50,
    "primary": 60, "primary_link": 40, "secondary": 50, "secondary_link": 40,
    "tertiary": 40, "tertiary_link": 30, "unclassified": 40,
    "residential": 30, "living_street": 20, "service": 20,
}
SERVICIOS_EXCLUIDOS = {"driveway", "parking_aisle", "drive-through", "emergency_access"}

RAIZ = Path(__file__).resolve().parents[1]
SALIDA_POR_DEFECTO = RAIZ / "data" / "huancayo_grafo.npz"


def consulta_overpass() -> str:
    tipos = "|".join(VELOCIDAD_KMH)
    s, o, n, e = CAJA
    return f'[out:json][timeout:120];way["highway"~"^({tipos})$"]({s},{o},{n},{e});(._;>;);out body;'


def descargar() -> dict:
    cuerpo = urllib.parse.urlencode({"data": consulta_overpass()}).encode()
    ultimo_error = None
    for url in ENDPOINTS:
        try:
            peticion = urllib.request.Request(url, data=cuerpo, headers={"User-Agent": "RouteZero-academico/1.0"})
            with urllib.request.urlopen(peticion, timeout=150) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001 - se prueba el siguiente servidor
            ultimo_error = exc
            print(f"  {url} falló ({exc}); se prueba el siguiente", file=sys.stderr)
            time.sleep(2)
    raise SystemExit(f"No se pudo descargar de Overpass: {ultimo_error}")


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radio = 6371000.0
    f1, f2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((f2 - f1) / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * radio * math.asin(math.sqrt(a))


def sentido_de(etiquetas: dict) -> int:
    """1 = solo en el sentido del dibujo, -1 = solo en el contrario, 0 = doble sentido."""
    oneway = etiquetas.get("oneway", "no")
    if oneway in ("yes", "true", "1") or etiquetas.get("junction") in ("roundabout", "circular"):
        return 1
    if oneway == "-1":
        return -1
    return 0


def transitable(etiquetas: dict) -> bool:
    if etiquetas.get("highway") not in VELOCIDAD_KMH:
        return False
    if etiquetas.get("access") in ("no", "private"):
        return False
    return etiquetas.get("service") not in SERVICIOS_EXCLUIDOS


def construir(datos: dict) -> dict:
    nodos = {e["id"]: (e["lat"], e["lon"]) for e in datos["elements"] if e["type"] == "node"}
    vias = [e for e in datos["elements"] if e["type"] == "way" and transitable(e.get("tags", {}))]

    indice: dict[int, int] = {}
    nombres: dict[str, int] = {"": 0}
    aristas = []  # (origen, destino, metros, segundos a velocidad base, id de nombre)
    for via in vias:
        etiquetas = via["tags"]
        sentido = sentido_de(etiquetas)
        velocidad_ms = VELOCIDAD_KMH[etiquetas["highway"]] / 3.6
        nombre_id = nombres.setdefault(etiquetas.get("name", ""), len(nombres))
        ids = [n for n in via["nodes"] if n in nodos]
        for a, b in zip(ids, ids[1:]):
            metros = haversine_m(*nodos[a], *nodos[b])
            if metros <= 0:
                continue
            for n in (a, b):
                indice.setdefault(n, len(indice))
            segundos = metros / velocidad_ms
            if sentido >= 0:
                aristas.append((indice[a], indice[b], metros, segundos, nombre_id))
            if sentido <= 0:
                aristas.append((indice[b], indice[a], metros, segundos, nombre_id))

    n = len(indice)
    origen = np.array([a[0] for a in aristas], dtype=np.int32)
    destino = np.array([a[1] for a in aristas], dtype=np.int32)
    metros = np.array([a[2] for a in aristas], dtype=np.float64)
    segundos = np.array([a[3] for a in aristas], dtype=np.float64)
    nombre_id = np.array([a[4] for a in aristas], dtype=np.int32)
    coords = np.zeros((n, 2), dtype=np.float64)
    for osm_id, i in indice.items():
        coords[i] = nodos[osm_id]

    # Solo la mayor componente fuertemente conexa: desde cualquier nodo se llega a cualquier otro.
    estructura = csr_matrix((np.ones(len(origen)), (origen, destino)), shape=(n, n))
    _, etiquetas_comp = connected_components(estructura, directed=True, connection="strong")
    mayor = np.bincount(etiquetas_comp).argmax()
    conserva = etiquetas_comp == mayor
    nuevo_indice = -np.ones(n, dtype=np.int64)
    nuevo_indice[conserva] = np.arange(conserva.sum())
    dentro = conserva[origen] & conserva[destino]

    return {
        "coords": coords[conserva].astype(np.float32),
        "u": nuevo_indice[origen[dentro]].astype(np.int32),
        "v": nuevo_indice[destino[dentro]].astype(np.int32),
        "dist": metros[dentro].astype(np.float32),
        "seg": segundos[dentro].astype(np.float32),
        "nombre_id": nombre_id[dentro],
        "nombres": np.array(list(nombres), dtype=str),
        "descartados": n - int(conserva.sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entrada", type=Path, help="JSON de Overpass ya descargado (evita la descarga)")
    parser.add_argument("--guardar-descarga", type=Path, help="guarda aquí el JSON descargado")
    parser.add_argument("--salida", type=Path, default=SALIDA_POR_DEFECTO)
    args = parser.parse_args()

    if args.entrada:
        datos = json.loads(args.entrada.read_text(encoding="utf-8"))
        print(f"Leído {args.entrada}")
    else:
        print("Descargando de Overpass (puede tardar unos segundos)…")
        datos = descargar()
        if args.guardar_descarga:
            args.guardar_descarga.write_text(json.dumps(datos), encoding="utf-8")

    grafo = construir(datos)
    meta = json.dumps(
        {"fuente": "OpenStreetMap contributors (ODbL)", "caja": CAJA, "generado": date.today().isoformat()},
        ensure_ascii=False,
    )
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    descartados = grafo.pop("descartados")
    np.savez_compressed(args.salida, meta=np.array(meta), **grafo)

    n, m = len(grafo["coords"]), len(grafo["u"])
    print(f"Grafo: {n} nodos y {m} tramos dirigidos ({descartados} nodos aislados descartados)")
    print(f"Calles con nombre: {len(grafo['nombres']) - 1}")
    print(f"Guardado en {args.salida} ({args.salida.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
