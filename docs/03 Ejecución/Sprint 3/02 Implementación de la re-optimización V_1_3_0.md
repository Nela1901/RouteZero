# 02 Implementación de la Re-optimización de Rutas

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Ítems** | HU-012 (Re-optimizar rutas ante evento de cambio operativo) y cierre de HT-07 |
| **Fecha** | 2026-10-20 |
| **Versión** | 1.3.0 |

[← Volver al README Principal](../../../README.md)

---

Este documento registra cómo se implementó la re-optimización de rutas (HU-012, RN-012) sobre el motor del Sprint 2, con las medidas reales. La medición en Render está en la sección 8.

## 1. Qué hace y cómo se usa

El administrador pide re-optimizar las rutas de una jornada cuando cambia algo: llega un pedido urgente, se cancela un pedido ya asignado o se reporta congestión en una vía. El sistema:

1. toma las rutas **en curso** (`CONFIRMADA` o `EN_EJECUCION`) de esa fecha; si no hay ninguna, responde que no hay rutas activas para re-optimizar y sugiere generar rutas (escenario 2);
2. **congela lo ya atendido** (paradas marcadas `ENTREGADO` o `FALLIDO`);
3. retira las paradas cuyo pedido se canceló e integra los pedidos `PENDIENTE` nuevos;
4. aplica los **incidentes de tráfico** activos;
5. calcula el plan de lo que falta, con cada vehículo partiendo de su última parada atendida (o del depósito si todavía no entregó nada) y desde la hora actual;
6. deja el resultado como **borrador por ruta**, que el administrador confirma o descarta con los mismos botones de siempre. Al confirmar, las paradas pendientes de cada ruta en curso se reemplazan por las nuevas.

El flujo borrador y confirmación es el mismo de la generación de rutas del Sprint 2: nada cambia en las rutas en curso hasta que el administrador confirma.

## 2. Cambios en el motor (`backend/src/algoritmo/`)

Todos los campos nuevos son opcionales: sin ellos el motor trabaja exactamente como en el Sprint 2 (las 30 pruebas anteriores del motor siguen pasando).

| Cambio | Dónde | Para qué |
|---|---|---|
| `Arranque` (nodo, hora de salida, trabajo acumulado) | `modelo.py`, `evaluacion.py` | Un vehículo ya en ruta parte de su último punto, a una hora dada y con su trabajo continuo ya acumulado (RN-003). La jornada sigue contando desde la salida original. |
| `pares_fijos` | `modelo.py`, `motor.py` | Se conservan los pares vehículo-conductor ya asignados; no se vuelve a emparejar. |
| `plan_vigente` | `motor.py` | Punto de partida: el plan que ya existe, sin las paradas que dejaron de existir, con los pedidos nuevos insertados donde menos cuestan. Si no es peor que la solución voraz, se parte de él. Una ruta que deja de ser válida (por ejemplo por un incidente) se descarta y sus pedidos se reparten de nuevo. |
| Matriz de feromonas del tamaño de la matriz de tiempos | `aco.py` | Incluye los nodos de arranque de los vehículos en ruta. |

Como el punto de partida es el plan vigente, el resultado de la re-optimización **nunca es peor** que continuar con él (comprobado por prueba).

## 3. Congestión por calle (`backend/src/red_vial/`)

- `Grafo.tiempo_con_congestion(factores)` multiplica el tiempo de los tramos de las calles indicadas. Un nombre coincide con todo tramo que lo contenga, sin distinguir mayúsculas ni tildes («giraldez» alcanza «Avenida Giraldez»).
- Solo cambia el **tiempo**, no la distancia. El camino más rápido rodea la calle congestionada si conviene.
- `RedVial.matrices(puntos, congestion=...)` y `calcular_matrices(..., congestion=...)`. Sin congestión se usa la matriz base, sin recalcular.
- `Grafo.tramos_de_calle(nombre)` devuelve los segmentos de una vía, para dibujarla en el mapa (HU-013).
- Tramos del grafo real por vía: Av. Ferrocarril 616 (578 con ese nombre y 38 como «Av. Ferrocarril»), Av. Giráldez 49, Calle Real 298.
- Solo se pueden reportar las tres vías de la RN-012 (Av. Ferrocarril, Av. Giráldez y Calle Real), con un factor de lentitud mayor que 1 y hasta 10.
- Desde HU-013 los incidentes también se aplican al **generar** rutas, y cada tramo usa los tiempos de hora punta si sale en una franja de RF-003 (ver [`04 Implementación del mapa de rutas`](04%20Implementaci%C3%B3n%20del%20mapa%20de%20rutas%20V_1_3_0.md)).

## 4. API

| Método y ruta | Rol | Qué hace |
|---|---|---|
| `POST /api/rutas/reoptimizar` | Administrador | Re-optimiza una fecha. Cuerpo: `fecha_jornada`, `tiempo_max_s` (tope 30) y `hora_actual` opcional (solo pruebas y demostraciones; sin ella se usa la hora real de Perú). Responde con el borrador, el resumen y `dentro_del_limite`. |
| `POST /api/rutas/lotes/{lote}/confirmar` | Administrador | Confirma una generación o una re-optimización (detecta cuál es). |
| `DELETE /api/rutas/lotes/{lote}` | Administrador | Descarta el borrador. |
| `PATCH /api/rutas/{ruta}/paradas/{pedido}/entrega` | Administrador, Operador | Marca una parada como `ENTREGADO` o `FALLIDO`. La ruta pasa a `EN_EJECUCION` y, al atender la última, a `COMPLETADA`. |
| `POST /api/rutas/incidentes` | Administrador | Registra una alerta de congestión. |
| `GET /api/rutas/incidentes` | Administrador, Operador, Conductor | Lista las alertas activas. |
| `DELETE /api/rutas/incidentes/{id}` | Administrador | Marca la alerta como resuelta. |

Además, `DELETE /api/pedidos/{id}` ahora también cancela un pedido `ASIGNADO` (antes respondía 409). Sus datos de base de datos están en [`11. Base de datos V_1_9_0`](../../01%20Inicio/historial%20Inicio/11.%20Base%20de%20datos%20V_1_9_0.md) y la migración en `backend/scripts/migracion_reoptimizacion.sql`.

## 5. Decisiones

| Decisión | Motivo |
|---|---|
| La re-optimización se confirma antes de aplicarse | Misma regla del Sprint 2: el administrador revisa antes de cambiar rutas que los conductores ya tienen. |
| Las entregas se registran de verdad (PATCH) en vez de suponerlas | «Sin alterar las entregas ya completadas» necesita saber cuáles lo están. Evita una demostración inventada. |
| La hora se toma del reloj, con un parámetro opcional de prueba | Fuera del horario laboral todas las ventanas ya habrían pasado y todo saldría atrasado. |
| Los incidentes se guardan como alerta activa | Los reutilizarán el mapa (HU-013) y la vista del conductor (HU-014). |
| El incidente no dispara la re-optimización por sí solo | El administrador decide cuándo recalcular; la re-optimización aplica los incidentes activos. |
| Operador y Administrador registran entregas | Funciona como un despacho que registra lo que reporta el conductor. El conductor lo hará por su cuenta en HU-014. |

## 6. Limitaciones conocidas

- Una entrega **fallida** deja el pedido `ASIGNADO` y no lo re-planifica solo.
- Tras re-optimizar, la distancia, el tiempo, la hora de regreso y las métricas de la ruta describen el tramo restante, no la ruta completa.
- La parada de un pedido cancelado sigue visible (tachada, como «Pedido cancelado») hasta que se confirma la re-optimización.
- `conductores.usuario_id` existe pero ninguna pantalla lo asigna; hace falta para que un conductor vea y marque su propia ruta (HU-014).
- Una sola generación o re-optimización a la vez por servidor (el mismo candado del Sprint 2).

## 7. Pruebas

| Capa | Archivo | Qué comprueba |
|---|---|---|
| Motor | `tests/test_algoritmo_reoptimizacion.py` (7) | Salida desde un punto y hora, pedido urgente integrado, pares fijos, incidente que triplica los tiempos, nunca peor que el plan vigente. |
| Red vial | `tests/test_red_vial_congestion.py` (7) | La congestión encarece el tiempo y no la distancia, el desvío, nombres sin tildes, tramos de una vía, y que el grafo real trae las tres vías. |
| Servicio y API | `tests/test_reoptimizacion.py` (11, contra la base real) | Escenario 1 (pedido urgente, dentro de 30 s y confirmado), escenario 2 (sin rutas activas), lo entregado no cambia, cancelación, incidentes, confirmación rechazada si cambió un pedido, descarte, ruta que termina, entregas y roles. |
| Frontend | `RutasPage.test.tsx` y `CrudPages.test.tsx` | Botón de re-optimizar por rol, resumen, borrador de re-optimización, entregas, incidentes y cancelación de pedidos asignados. |

Resultados al 20-10-2026:

- Suite completa del backend: **288 pruebas pasan, cobertura total de 98 %** (96 % al cierre del Sprint 2). Después se agregó `pedido_estado` a las paradas y se repitieron las pruebas de rutas, re-optimización, pedidos y arquitectura: 58 pasan.
- Frontend: **60 pruebas pasan** y el `npm run build` completo termina sin errores.
- Bandit sin hallazgos medios ni altos en el código nuevo.

Un fallo real encontrado por las pruebas: al confirmar, una ruta sin paradas por atender debía quedar `COMPLETADA`, pero el código contaba también las ya entregadas. Se corrigió contando solo las pendientes.

## 8. Rendimiento (RN-012: 30 s)

Benchmark local (`tests/test_benchmark_reoptimizacion.py`, `pytest -m benchmark -s --no-cov`): 150 pedidos y 15 vehículos sobre el grafo real, con las dos primeras paradas de cada ruta ya entregadas, 10 pedidos urgentes nuevos y congestión en Av. Ferrocarril (×3) y Av. Giráldez (×2). El total suma 5 s de reserva para guardar el borrador.

| Semilla | Pedidos a planificar | Matrices | Motor | Total con reserva | Rutas | Sin cobertura |
|---|---|---|---|---|---|---|
| 1 | 132 | 0.8 s | 15.7 s | 21.6 s | 14 | 0 |
| 2 | 130 | 0.8 s | 8.7 s | 14.5 s | 14 | 0 |
| 3 | 134 | 0.8 s | 9.0 s | 14.8 s | 13 | 1 |

Los tres casos cumplen el límite en la máquina de desarrollo.

### 8.1 Medición en Render (20-10-2026)

Servicio gratuito de Render (0.1 de CPU), base de datos en Supabase y el endpoint real `POST /api/rutas/reoptimizar`. Escenario: 150 pedidos pendientes y 15 vehículos con 15 conductores (se completaron con datos temporales, ya borrados), rutas generadas y confirmadas en una fecha lejana (14 rutas, 150 paradas, 29.8 s), 28 entregas ya registradas, 10 pedidos urgentes nuevos, congestión en Av. Ferrocarril (×3) y Av. Giráldez (×2) y hora de referencia 10:00. Cada borrador se descartó al terminar. El script es `backend/tests_manual/medir_reoptimizacion_render.py` (local, no versionado).

| Corrida | Servidor (s) | Petición completa (s) | Matrices | Motor | Guardado | Iteraciones | Rutas | Paradas | Sin cobertura | Dentro de 30 s |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.2 | 29.0 | 9.3 | 14.7 | 1.3 | 9 | 14 | 132 | 0 | sí |
| 2 | 27.1 | 29.0 | 9.6 | 14.3 | 1.3 | 7 | 14 | 132 | 0 | sí |
| 3 | 27.1 | 29.0 | 9.4 | 14.5 | 1.3 | 8 | 14 | 132 | 0 | sí |
| 4 | 27.2 | 29.1 | 9.2 | 14.8 | 1.3 | 8 | 14 | 132 | 0 | sí |
| 5 | 27.2 | 29.0 | 9.4 | 14.6 | 1.2 | 8 | 14 | 132 | 0 | sí |

**La re-optimización cumple la RN-012 en Render: 27.1 a 27.2 s dentro del servidor y 29.0 a 29.1 s medidos desde un equipo externo** (la lectura de datos toma unos 1.9 s y el resto es respuesta y red). Los 132 pedidos a planificar, entre ellos los 10 urgentes, se atendieron en todas las corridas.

Observaciones:

- **El margen era corto** (cerca de 1.0 s medidos desde fuera). Se amplió: el presupuesto por defecto baja a **25 s** y los 30 s quedan como el límite que informa `dentro_del_limite`. En el equipo de desarrollo, con 150 pedidos y 15 vehículos, la re-optimización pasó a 17.9–22.8 s en total con la reserva de guardado (ver [`04 Implementación del mapa de rutas`](04%20Implementaci%C3%B3n%20del%20mapa%20de%20rutas%20V_1_3_0.md)). Confirmado en Render el 20-10-2026: **22.2 s en el servidor y 24.0 s desde fuera**, con la segunda matriz de hora punta incluida (sección 8.1 de [`04 Implementación del mapa de rutas`](04%20Implementaci%C3%B3n%20del%20mapa%20de%20rutas%20V_1_3_0.md)).
- **Las matrices pesan 9.2 a 9.6 s** (el tiempo con congestión se calcula con el grafo completo), igual que en la generación del Sprint 2 (IMP-013).
- **El ACO rinde poco en Render:** 7 a 9 iteraciones, como en el Sprint 2. Por eso la re-optimización parte del plan vigente: el resultado nunca es peor que continuar con él.

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: motor, congestión por calle, API, decisiones, limitaciones, pruebas y benchmark local de la re-optimización (HU-012) | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-20 | Se agrega la medición en Render de la re-optimización (150 pedidos, 15 vehículos, 5 corridas) con sus observaciones y la propuesta de ampliar el margen | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-20 | Se amplía el margen de la re-optimización (presupuesto de 25 s) y se aclara que los incidentes y las horas punta también se aplican al generar | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-20 | Se confirma en Render el nuevo margen de la re-optimización: 22.2 s en el servidor y 24.0 s desde fuera | Inciso Aguilar Elizabeth Antonela |
