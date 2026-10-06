# 02 Implementación del Motor de Rutas

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03 oct – 16 oct 2026) |
| **Cambio OpenSpec** | `add-motor-rutas` ([`openspec/changes/add-motor-rutas/`](../../../openspec/changes/add-motor-rutas/)) |
| **Fecha** | 2026-10-05 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

Este documento registra cómo se implementó el motor de rutas (HU-011, HT-07 y HT-08), con las medidas reales de cada pieza. Se completa a medida que avanzan los grupos de tareas del cambio.

## 1. Red vial

### 1.1 Procedencia de los datos

Las distancias y tiempos de viaje se calculan sobre un grafo dirigido de las calles de la zona urbana de Huancayo, Chilca y El Tambo (caja de -12.12 a -11.99 de latitud y de -75.27 a -75.17 de longitud), construido con datos de **OpenStreetMap** obtenidos de la API Overpass.

**Crédito obligatorio (licencia ODbL): © OpenStreetMap contributors.**

El archivo `backend/data/huancayo_grafo.npz` se versiona en el repositorio; en ejecución el backend solo lo lee y **no llama a ningún servicio externo**.

### 1.2 Cómo regenerar el grafo

Desde `backend/`:

```bash
python scripts/generar_grafo.py                       # descarga de Overpass y genera el archivo
python scripts/generar_grafo.py --entrada osm.json    # reconstruye desde una descarga guardada
python scripts/generar_grafo.py --guardar-descarga osm.json
```

El script conserva solo las vías transitables por vehículos (`motorway` a `service`, sin accesos privados ni entradas de garaje o estacionamientos), respeta los sentidos únicos y las rotondas, y se queda con la **mayor componente fuertemente conexa**, de modo que desde cualquier nodo se llega a cualquier otro. Regenerarlo con la misma descarga produce un archivo idéntico, y descargar de nuevo (05-10-2026) devolvió las mismas cifras.

### 1.3 Velocidades y tiempos

Cada tramo recibe una velocidad base según su tipo de vía, alineada con el Reglamento Nacional de Tránsito (DS 033-2001-MTC, art. 162: 40 km/h en calles y jirones, 60 km/h en avenidas, 80 km/h en vías expresas):

| Tipo de vía | km/h | Tipo de vía | km/h |
|---|---|---|---|
| `motorway` / `trunk` / `primary` | 80 / 60 / 60 | `tertiary` / `unclassified` | 40 |
| `secondary` | 50 | `residential` | 30 |
| `*_link` | 30–60 | `living_street` / `service` | 20 |

El tiempo en ejecución es el tiempo a velocidad base dividido por un **factor de velocidad urbana de 0.6** (`factor_velocidad_urbana` en `config.py`), que refleja tráfico, semáforos y paradas. Es un supuesto a calibrar con datos reales.

### 1.4 Cálculo de matrices

- Cada punto (depósito y pedidos) se asigna al **nodo más cercano** con un árbol KD. Si está a más de **500 m** de una calle, ese punto usa **línea recta × 1.35** (resultado marcado como fuente `mixta` o `aproximada`).
- Para los demás se calcula el camino más corto con Dijkstra, **por bloques de 25 fuentes**, y se suma el tramo de acceso entre el punto y su nodo.
- Las matrices de distancia y de tiempo se calculan por separado (camino más corto por distancia y por tiempo). Es una simplificación: ambos caminos pueden diferir.
- Si el archivo del grafo falta o está dañado, todo el cálculo usa el respaldo en línea recta × 1.35 y el resultado lo informa.
- Si varios tramos unen el mismo par de nodos se conserva el más corto (por defecto `scipy` sumaría los duplicados).

### 1.5 Resultados medidos

| Medida | Resultado |
|---|---|
| Descarga de OpenStreetMap | 5.2 MB en unos 3 s |
| Grafo | 37,573 nodos y 82,569 tramos dirigidos (293 nodos aislados descartados) |
| Archivo del grafo | **0.75 MB** |
| Calles con nombre | 1,958 nombres distintos |
| Avenidas de los requisitos | Av. Ferrocarril (616 tramos), Calle Real (298) y Av. Giráldez (49) |
| Matriz de 151 × 151 (150 pedidos y el depósito, distancias y tiempos) | **0.96 a 1.33 s** en un equipo de desarrollo; sin pares inalcanzables |
| Memoria adicional del cálculo (pico medido con `tracemalloc`) | **8 MB** |
| Distancia por calles frente a línea recta | ~1.38 de media y 1.30 de mediana (80 % de los pares entre 1.12 y 1.68) |

Calidad de los datos de la zona: 7,546 vías, el 58 % con nombre (el 99 % de las primarias y el 84 % de las secundarias), solo el 4 % con límite de velocidad y el 8 % con sentido único marcado. Por eso se usan velocidades por tipo de vía, y un sentido único faltante podría proponer un giro prohibido; se verificará visualmente cuando exista el mapa de rutas (Sprint 3).

Pendiente de medir: el mismo cálculo en Render gratuito (0.1 de CPU), que podría tardar hasta unas diez veces más; sigue lejos del límite de 45 s, pero se registrará en la tarea de cierre del cambio.

### 1.6 Pruebas

`backend/tests/test_red_vial.py` cubre: sentidos únicos respetados, forma de la matriz y diagonal cero, pedidos en el mismo lugar, tramo de acceso, respaldo con archivo ausente o dañado, puntos a más de 500 m de la red, avenida más rápida que calle residencial, escala del factor de velocidad, tramos duplicados, carga única del grafo y, con el archivo real, cobertura del depósito, coherencia con la línea recta y presencia de las tres avenidas. La prueba de rendimiento (marca `benchmark`) se ejecuta con `pytest -m benchmark`. Cobertura del módulo `red_vial`: 100 %.

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: sección de red vial (procedencia de los datos, regeneración, velocidades, matrices y resultados medidos) | Inciso Aguilar Elizabeth Antonela |
