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
| **Versión** | 1.2.0 |

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

## 2. Algoritmo de optimización (ACO)

El motor vive en `backend/src/algoritmo/` y es **Python puro con `numpy`**: no importa FastAPI, SQLAlchemy ni ningún otro módulo del backend (lo vigila `tests/test_arquitectura.py`). Recibe un `Problema` (pedidos, vehículos, conductores, matrices de distancia y tiempo, parámetros) y devuelve un `Resultado`. Los instantes son segundos desde la medianoche, las distancias son metros y el índice 0 de las matrices es el depósito.

### 2.1 Reglas de negocio y cómo se aplican

| Regla | Aplicación en el motor |
|---|---|
| RN-005 Capacidad | Dura: una parada solo se agrega si el peso acumulado no supera la capacidad del vehículo |
| RN-002 Jornada máxima | Dura: la ruta termina antes de `min(salida + 8 h, fin del horario del conductor)` |
| RN-003 Descanso | Se inserta un descanso de 60 min antes de un tramo si el trabajo continuo (viaje y atención, sin contar esperas) superaría 4 h |
| RN-006 Ventanas de tiempo | Blanda: si se llega antes se espera hasta que abra; el retraso se penaliza por minuto |
| RN-008 Express | Penalización de retraso ×5 (EXPRESS), ×1 (ESTANDAR) y ×0.5 (ECONOMICO); mientras quede un EXPRESS que quepa en la ruta, solo se consideran EXPRESS, de modo que van primero |
| RN-009 CO₂ | `distancia (km) × factor de emisión` del vehículo |
| RN-004 Restricción por placa | Tabla opcional dígito → días de la semana, **desactivada por defecto** (ver la corrección de la cita normativa en `09. Reglas de negocio V_1_1_0`) |
| RN-015 Tiempo | Presupuesto de 30 s por defecto (máximo 40 s); la búsqueda devuelve lo mejor encontrado al agotarse |

### 2.2 Elegibilidad y emparejamiento

Solo entran vehículos en estado `DISPONIBLE` sin restricción de circulación ese día, y conductores disponibles con la licencia vigente en la fecha de la jornada (vencida o que vence ese mismo día no sirve). Cada vehículo se empareja con un conductor de categoría compatible: las `A-*` conducen CAMIONETA y FURGON; las `B-IIa` y `B-IIb`, MOTO (**supuesto del diseño**). Como cada categoría solo maneja una familia de vehículos, el emparejamiento voraz forma el máximo de pares posible; dentro de cada familia el vehículo de mayor capacidad recibe al conductor con la disponibilidad más amplia. Los pares se ordenan del más eficiente al menos eficiente (costo por kilómetro de distancia, combustible y CO₂).

### 2.3 Itinerario de una ruta

La ruta sale a `max(08:00, inicio del conductor)`. En cada parada: viaje, espera si la ventana aún no abre, **10 minutos fijos de atención** y retraso si se atiende después del cierre de la ventana. `simular_ruta` es la referencia exacta de estos cálculos; la construcción vectorizada replica sus reglas y las pruebas comprueban que ambas coinciden (toda ruta devuelta se vuelve a simular y es válida).

### 2.4 Función objetivo

`costo = 1.0·km + 1.0·litros + 2.0·kg de CO₂ + 0.5·Σ(ponderación de prioridad · minutos de retraso)`, más 1,000 por cada pedido sin asignar (multiplicado por la ponderación de su prioridad), de modo que cubrir un pedido siempre conviene más que dejarlo fuera. Todos los pesos son parámetros (`Parametros`); son valores iniciales a calibrar, no requisitos normativos.

### 2.5 Búsqueda

1. **Solución voraz**: para cada vehículo se arma la ruta agregando siempre el mejor candidato factible (menor costo incremental y ventana más urgente). Es la línea base y garantiza una respuesta válida.
2. **ACO tipo ACS**: 20 hormigas, α = 1, β = 3, evaporación 0.1 y regla pseudoaleatoria proporcional con q0 = 0.9. La visibilidad es `1 / (costo incremental + 0.5·holgura de la ventana en horas + 0.01)`. Se aplica solo la actualización global (la mejor solución refuerza sus arcos con `ρ / costo`); no se aplica la actualización local por paso del ACS original, para simplificar.
3. **Mejora local** (primera mejora): inserción de pedidos sin asignar, 2-opt dentro de cada ruta y reubicación de paradas entre rutas, siempre comprobada con `simular_ruta`. Se aplica a cada nueva mejor solución (con 300 evaluaciones como máximo) y al final, con el 15 % del tiempo reservado.
4. **Parada**: presupuesto de tiempo, 50 iteraciones sin mejora o 500 iteraciones. Con `tiempo_max_s = None` y una semilla, el resultado es **reproducible**.
5. La solución devuelta nunca es peor que la voraz.

### 2.6 Pedidos sin cobertura

Cada pedido que no se asigna recibe un motivo y una sugerencia: `PESO_EXCEDE_CAPACIDAD` (mayor que cualquier vehículo), `SIN_RECURSOS` (no hay pares vehículo-conductor; en ese caso el resultado se marca `imposible`), `FUERA_DE_JORNADA` (no cabe ni solo en ninguna jornada) o `FLOTA_INSUFICIENTE`.

### 2.7 Supuestos pendientes de calibrar

Tiempo de atención de 10 min fijos (sin datos reales de Andina; ver la sensibilidad abajo), factor de velocidad urbana de 0.6, compatibilidad licencia-vehículo, pesos de la función objetivo, ponderaciones de prioridad, inicio de jornada a las 08:00 y un único depósito.

### 2.8 Resultados del benchmark (equipo de desarrollo)

Escenario: 150 pedidos aleatorios dentro de Huancayo (10 a 200 kg, ventanas de 2 a 4 h que abren entre las 08:00 y las 12:00, 10 % EXPRESS), 15 vehículos de 500 a 3,000 kg y 15 conductores con horario de 06:00 a 14:00, con **distancias por calles reales** y el presupuesto de 30 s por defecto. Cada corrida incluye el cálculo de matrices.

| Corrida | Total (s) | Iteraciones | Rutas | Atendidos | Mejora de costo sobre la voraz |
|---|---|---|---|---|---|
| 1 | 19.9 | 127 | 14 | 150/150 | 40 % |
| 2 | 7.6 | 55 | 15 | 150/150 | 26 % |
| 3 | 15.3 | 119 | 13 | 150/150 | 31 % |
| 4 | 27.2 | 183 | 13 | 150/150 | 40 % |
| 5 | 11.1 | 52 | 13 | 150/150 | 69 % |
| 6 | 9.0 | 52 | 14 | 150/150 | 64 % |
| 7 | 9.7 | 65 | 15 | 150/150 | 47 % |
| 8 | 16.7 | 120 | 14 | 150/150 | 25 % |
| 9 | 8.4 | 54 | 14 | 150/150 | 46 % |
| 10 | 12.4 | 88 | 14 | 150/150 | 77 % |

**Percentil 95 del tiempo total: 23.9 s** (límite de RN-015: 45 s); máximo 27.2 s y mediana 11.8 s. La búsqueda suele terminar antes del presupuesto porque se detiene tras 50 iteraciones sin mejora. En las diez corridas se atendieron los 150 pedidos. **Pendiente**: repetir la medición en Render gratuito (0.1 de CPU), donde habrá menos iteraciones por segundo y la solución podría ser menos pulida.

### 2.9 Sensibilidad del tiempo de atención por parada

Mismo escenario (semilla 3) con presupuesto de 10 s:

| Atención por parada | Rutas usadas | Atendidos | Entregas tardías | Distancia (km) | CO₂ (kg) | Costo |
|---|---|---|---|---|---|---|
| 5 min | 10 | 150 | 0 | 345.7 | 76.6 | 534 |
| **10 min (valor de diseño)** | 13 | 150 | 2 | 344.6 | 80.5 | 541 |
| 15 min | 15 (toda la flota) | 150 | 1 | 365.4 | 90.8 | 585 |

El tiempo de atención no cambia mucho la distancia total, pero sí **cuántos vehículos hacen falta** (10, 13 y 15) y, con ello, las emisiones (+5 % y +19 % de CO₂ respecto de 5 min). Con 15 minutos se usa toda la flota: un tiempo mayor dejaría pedidos sin cobertura. Por eso conviene calibrar este valor con datos reales de la empresa.

### 2.10 Pruebas

`backend/tests/test_algoritmo.py` (30 pruebas): itinerarios calculados a mano (espera, retraso por prioridad, descanso, jornada, capacidad y orden express), elegibilidad (licencia vencida, categoría incompatible, estados, restricción por placa), solución voraz (cobertura única, capacidad y express primero), ACO (nunca peor que la voraz, mejora en un caso con margen, reproducibilidad, presupuesto de tiempo, preferencia por el vehículo de menor emisión) y pedidos sin cobertura (los cuatro motivos y el caso sin pedidos). Cobertura del paquete `algoritmo`: entre 89 % y 100 % por archivo. El benchmark (`tests/test_benchmark_motor.py`, marca `benchmark`) se ejecuta con `pytest tests/test_benchmark_motor.py -m benchmark -s --no-cov`.

## 3. Módulo de rutas (backend)

`backend/src/rutas/` (router → servicio → repositorio) conecta el motor con la base de datos. Usa solo `core`, `auditoria`, `red_vial` y `algoritmo`; sus consultas sobre pedidos, vehículos y conductores son propias, de modo que no depende del código de otros módulos de negocio.

### 3.1 API

| Método y ruta | Rol | Función |
|---|---|---|
| `POST /api/rutas/generar` | Administrador | Genera rutas en borrador para todos los pedidos `PENDIENTE` |
| `POST /api/rutas/lotes/{lote_id}/confirmar` | Administrador | Rutas a `CONFIRMADA` y pedidos a `ASIGNADO` |
| `DELETE /api/rutas/lotes/{lote_id}` | Administrador | Descarta un lote de borradores |
| `GET /api/rutas?fecha=` | Administrador y Operador | Rutas de una fecha, con métricas |
| `GET /api/rutas/{ruta_id}` | Administrador y Operador | Detalle con las paradas en orden y su hora estimada |

### 3.2 Reglas y decisiones de implementación

- **Borrador y confirmación**: generar no cambia el estado de los pedidos. Regenerar para una fecha reemplaza **solo** los borradores `PLANIFICADA` de esa fecha (con un candado de transacción por fecha) y deja las rutas confirmadas intactas; como los pedidos confirmados pasan a `ASIGNADO`, el nuevo borrador solo considera pedidos aún pendientes.
- **Confirmar** bloquea las filas de los pedidos del lote (`FOR UPDATE`) y exige que todos sigan `PENDIENTE`; si alguno fue cancelado durante la revisión responde 409 con los identificadores afectados y la indicación de regenerar. No se escribe nada antes de comprobarlo.
- **Una generación a la vez** por proceso (candado en memoria): una segunda solicitud simultánea recibe 409.
- **Transacción corta**: el servicio lee los datos, hace `commit()` y calcula sin transacción abierta (el cálculo puede durar hasta 40 s); después reaplica el contexto RLS (`reaplicar_contexto_rls`) para escribir. Es una excepción documentada a la convención de un único commit por petición, aceptable porque estas tablas tienen política permisiva.
- **Presupuesto de tiempo**: el solicitado (30 s por defecto, tope de 40 s) incluye la lectura y el cálculo de matrices; el motor recibe lo que queda.
- **Fecha de la jornada**: no puede ser pasada, y "hoy" se calcula en horario de Perú (UTC-5) porque Render corre en UTC.
- **Sin recursos**: si no hay vehículos y conductores elegibles, la respuesta es `imposible` con todos los pedidos sin cobertura, y los borradores anteriores se conservan.
- **Métricas por ruta**: CO₂, combustible, distancia y porcentaje de entregas dentro de ventana; el combustible ahorrado frente a la solución voraz se reparte entre las rutas en proporción a su consumo.
- **Auditoría**: `ruta_generada`, `ruta_confirmada` y `ruta_descartada`, con el identificador del lote como único detalle (sin nombres ni DNI).

### 3.3 Pruebas

`backend/tests/test_rutas.py` (18 pruebas contra la base real): generación de borrador sin cambiar pedidos, fecha pasada, regeneración, pedido más pesado que la flota, sin vehículos conservando borradores, licencia que vence el mismo día, generación simultánea (409), confirmación (con auditoría), pedido cancelado durante la revisión, confirmación repetida o de un lote inexistente, regeneración con rutas confirmadas, descarte de borradores y de rutas confirmadas, y el flujo completo por la API con el control de acceso por rol. Las pruebas crean sus propios clientes, pedidos, vehículos y conductores y limitan el motor a ellos (no alteran los datos reales); usan una fecha a 200 días y borran todo al terminar.

## 4. Escalabilidad de la API (HT-08)

### 4.1 Independencia de módulos

La zona de cobertura (RN-007) pasó de `clientes` a `core/zona.py` y `pedidos` verifica la existencia del cliente con su propia consulta. `tests/test_arquitectura.py` analiza las importaciones con `ast` y falla si un módulo de negocio importa a otro (salvo `core` y `auditoria`) o si `algoritmo` importa FastAPI, SQLAlchemy u otro módulo del backend.

### 4.2 Paginación del listado de pedidos

`GET /api/pedidos` devuelve `{items, total, limite, desplazamiento}`: 50 pedidos por defecto y 200 como máximo (un límite mayor se rechaza con 422 indicando el máximo), ordenados del más reciente al más antiguo y con el total que cumple el filtro. Cambio de contrato: el frontend se adapta en el grupo de tareas de la interfaz.

### 4.3 Índices

El índice compuesto `idx_pedidos_estado_creado (estado, creado_en DESC)` se agregó para este listado; los índices por `estado`, `prioridad` y `cliente_id` ya existían. Con 1,002 pedidos, `EXPLAIN ANALYZE` del listado de pendientes muestra `Index Scan using idx_pedidos_estado_creado` (con un ordenamiento incremental) y 0.2 ms de ejecución.

### 4.4 Prueba de carga con 1,000 pedidos

`tests/test_carga_pedidos.py` (marca `carga`; se ejecuta con `pytest tests/test_carga_pedidos.py -m carga -s --no-cov`) inserta 1,000 pedidos y mide la API completa (autenticación, sesión de base de datos y consulta) contra Supabase real:

| Operación | Muestras | Mediana | Percentil 95 | Máximo |
|---|---|---|---|---|
| Consulta (página de 50, filtro por estado) | 30 | 1.05 s | **1.06 s** | 1.06 s |
| Registro de pedido | 15 | 1.13 s | **1.14 s** | 1.15 s |
| Cancelación de pedido | 15 | 1.06 s | **1.08 s** | 1.09 s |

Se cumple el límite de 2 s del percentil 95 (RNF-008). Una observación importante: las tres operaciones tardan casi lo mismo (~1.05 s), lo que indica que el tiempo **no depende del número de pedidos sino de la latencia de red hacia la base de datos remota**: cada petición hace varios viajes secuenciales a Supabase (verificación del usuario y de la sesión, y la consulta). La medición se hizo desde un equipo de desarrollo; el valor en Render dependerá de la distancia entre Render y Supabase. Una mejora posible, fuera del alcance de este cambio, es reducir esos viajes (por ejemplo, reutilizando la misma sesión de base de datos para la autenticación y la consulta).

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: sección de red vial (procedencia de los datos, regeneración, velocidades, matrices y resultados medidos) | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-05 | Se agrega la sección del algoritmo de optimización (reglas, elegibilidad, itinerario, función objetivo, búsqueda, supuestos), los resultados del benchmark de 150 pedidos y 15 vehículos y la sensibilidad del tiempo de atención por parada | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-05 | Se agregan el módulo de rutas del backend (API, reglas y decisiones de implementación, pruebas) y la escalabilidad de la API (independencia de módulos, paginación, índices y prueba de carga con 1,000 pedidos) | Inciso Aguilar Elizabeth Antonela |
