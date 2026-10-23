# 04 Implementación del Mapa de Rutas y la Congestión por Horas Punta

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Ítems** | HU-013 (Visualizar rutas optimizadas en mapa interactivo) y la congestión por horas punta de RF-003 |
| **Fecha** | 2026-10-20 |
| **Versión** | 1.2.0 |

[← Volver al README Principal](../../../README.md)

---

Este documento registra cómo se implementó el mapa de rutas (HU-013), el trazado por calles reales y la congestión por horas punta que pide RF-003. La medición en Render está en la sección 8.1.

## 1. Qué hace

- **Escenario 1 (rutas generadas):** el mapa dibuja el recorrido de cada ruta **por las calles de Huancayo**, las paradas numeradas con su estado, el tiempo estimado y la distancia de cada tramo, y las tres vías de la RN-012 coloreadas según su nivel de congestión (verde, amarillo o rojo).
- **Escenario 2 (sin rutas):** muestra el mapa base, el depósito, las vías y los pedidos pendientes, con un mensaje de que no hay rutas para esa fecha.
- **Monitoreo:** botón Actualizar y refresco automático cada 30 s (se puede desactivar).
- **Quién lo ve:** Administrador y Operador. El conductor tendrá su propia vista en HU-014.

## 2. Congestión por horas punta (RF-003)

**Problema.** El motor usaba un solo tiempo de viaje entre cada par de puntos, igual a las 8:00 que a las 12:30.

**Solución.** Dos matrices de tiempo: la normal y la de **hora punta**, con las tres vías más lentas. Al simular una ruta, cada tramo usa la matriz que corresponde **a la hora en que sale**. Como el motor busca el camino más rápido con esos tiempos, rodea solo las vías congestionadas cuando conviene (escenario de rutas alternativas de RF-003). Las distancias no cambian.

| Elemento | Valor | Origen |
|---|---|---|
| Franjas de hora punta | 7:30–9:30, 12:00–14:30 y 17:00–21:00 | RF-003 |
| Factor de hora punta, Av. Ferrocarril | ×1.8 | **Supuesto** |
| Factor de hora punta, Av. Giráldez | ×1.6 | **Supuesto** |
| Factor de hora punta, Calle Real | ×1.3 | **Supuesto** |
| Incidente de tráfico | factor registrado (hasta ×10); se **multiplica** con el de hora punta | HU-012, RN-012 |
| Nivel verde / amarillo / rojo | factor efectivo = 1 / menor que 2 / 2 o más | Decisión del 20-10-2026 |

No hay datos reales de tráfico de Huancayo: los factores de hora punta son **supuestos pendientes de calibrar**, igual que el tiempo de atención de 10 minutos. Se ajustan en `FACTOR_PUNTA` de `backend/src/rutas/congestion.py`.

La jornada de 8:00 a 14:00 queda dividida en tres franjas: punta (8:00–9:30), fluida (9:30–12:00) y punta (12:00–14:00). La franja de 17:00 a 21:00 no afecta a las rutas porque los conductores terminan a las 14:00, pero el mapa sí la muestra si se elige esa hora.

## 3. Cambios en el motor

Todos los campos nuevos son opcionales: sin franjas o sin la matriz de punta, el motor se comporta como antes (las pruebas anteriores siguen pasando).

| Cambio | Dónde | Para qué |
|---|---|---|
| `Parametros.franjas_punta` y `Problema.tiempo_punta_s` | `modelo.py` | Entradas de las franjas y de la matriz de punta. |
| `Datos.t_en`, `tl_en`, `vuelta_en` | `evaluacion.py` | Eligen la matriz según la hora de salida del tramo. |
| `simular_ruta` | `evaluacion.py` | Referencia exacta: el tramo usa la matriz de su hora; tras un descanso se vuelve a elegir, porque sale más tarde. |
| `construir` | `construccion.py` | Versión vectorizada del ACO con las mismas reglas. Una prueba comprueba que ninguna ruta armada se descarte por inválida al simularla, con franjas y descansos de por medio. |
| `calcular_matrices(..., congestion_punta=)` | `red_vial/matrices.py` | Segunda matriz de tiempos con los factores de punta. |

El costo medido de la segunda matriz con 151 puntos es de **0.85 a 1.3 s** en el equipo de desarrollo (+0.44 s); en Render se espera un aumento de unos 4 s.

La **generación** de rutas ahora también aplica los incidentes activos (antes solo la re-optimización los usaba).

## 4. Trazado por calles (`backend/src/rutas/trazado.py`)

- Para cada tramo (depósito → parada 1 → … → depósito) se calcula el camino más rápido sobre el grafo con una pasada de Dijkstra por grupo de tramos que comparten matriz (normal o de punta) y se reconstruye con los predecesores.
- La línea empieza y termina en las coordenadas reales de las paradas. La distancia es la longitud de esa línea y el tiempo sale del camino más rápido más el acceso desde el punto a la calle, igual que en el motor.
- Se simplifica con Douglas-Peucker (3 m) para reducir el tamaño de la respuesta.
- Si un punto no tiene calle cerca (a más de 500 m) o no hay camino, el tramo cae a línea recta con la velocidad de respaldo, igual que las matrices.
- Cada ruta se calcula una vez y se guarda en una caché en memoria con clave según sus paradas en orden y los incidentes vigentes, porque el mapa vuelve a pedir los datos cada 30 s.
- Costo medido: unos 36 ms por ruta de 12 paradas en el equipo de desarrollo.

## 5. API

| Método y ruta | Rol | Qué devuelve |
|---|---|---|
| `GET /api/rutas/mapa?fecha=` | Administrador, Operador | Rutas de la fecha (sin las canceladas, con los borradores) con paradas (estado de entrega y del pedido) y tramos (puntos, distancia, duración y si sale en hora punta), más el depósito. |
| `GET /api/rutas/congestion?hora=` | Administrador, Operador, Conductor | Las tres vías con nivel, factor efectivo, motivo (hora punta, incidente o ambos) y sus segmentos. Sin `hora`, la hora actual de Perú. |

## 6. Pantalla (`MapaPage`)

- Selector de fecha y de hora de la congestión, botón Actualizar, refresco automático de 30 s y filtro de pedidos pendientes.
- Un botón **Ocultar panel / Mostrar panel**: en pantallas angostas el panel empieza cerrado para no tapar el mapa.
- Cada ruta con un color de una paleta apta para daltonismo; los borradores con línea discontinua. Al pulsar un tramo se ve su tiempo y su distancia; al pulsar una parada, el cliente, la hora estimada y el estado.
- Estados de parada visibles: ✓ entregada, ✗ fallida, ✕ pedido cancelado y color de la ruta si está pendiente.
- Las tres vías se pintan según su nivel a la hora elegida.
- Panel accesible (no depende solo del mapa) con la lista de rutas, el tiempo y la distancia de cada tramo, el nivel de cada vía, la leyenda y la opción de mostrar u ocultar cada ruta. En pantalla pequeña el panel se ajusta al ancho.
- Mientras calcula los recorridos muestra un aviso (la primera carga en Render tarda unos 9 s) y después la hora de la última actualización.

## 7. Decisiones y limitaciones

| Decisión | Motivo |
|---|---|
| Congestión por franjas horarias y no solo por incidentes | RF-003 nombra las horas punta; el diseño del Sprint 2 las dejó para este sprint. |
| Recorrido por calles reales y no líneas rectas | Coincide con los tiempos que usa el motor. |
| Refresco automático cada 30 s sin websockets | Suficiente para el monitoreo que pide la historia y mucho más simple. |

Limitaciones:

- Los factores de hora punta son supuestos sin datos reales.
- La hora punta de un tramo se decide por la hora en que **sale**; un tramo largo que cruza el fin de una franja no se divide.
- La duración que muestra el trazado es de **viaje**; no incluye esperas por ventana de tiempo, la atención en cada parada ni los descansos.
- El mapa estima la hora de salida de cada tramo con la hora estimada de llegada más la atención; en rutas re-optimizadas puede diferir ligeramente del plan.
- El rendimiento de Lighthouse en producción queda por medir (con la API simulada la pantalla da 96 en móvil y 100 en escritorio; ver [`06 Calidad de la interfaz y pruebas de extremo a extremo`](06%20Calidad%20de%20la%20interfaz%20y%20pruebas%20de%20extremo%20a%20extremo%20V_1_0_0.md)).

## 8. Pruebas y rendimiento

| Capa | Archivo | Qué comprueba |
|---|---|---|
| Motor | `tests/test_algoritmo_punta.py` (6) | El tramo usa la matriz de su franja, el siguiente depende de su hora de salida, sin franjas el resultado es el de siempre y la construcción coincide con la simulación. |
| Red vial | `tests/test_red_vial_congestion.py` | Matriz de hora punta solo si se pide, y que no cambia la normal. |
| Trazado y niveles | `tests/test_trazado.py` (12) | Empalme con las paradas, rodeo por incidente, tramos en punta, línea recta de respaldo, simplificación, franjas de RF-003 y niveles. |
| Servicio y API | `tests/test_mapa.py` (contra la base real) | Un tramo por parada más el regreso, caché, niveles según hora e incidente, y roles. |
| Frontend | `MapaPage.test.tsx` (16) | Rutas, colores, borradores, estados de parada, congestión, hora, fecha, ocultar rutas, refresco automático y error. |

Resultados al 20-10-2026:

- Suite completa del backend: **313 pruebas pasan, cobertura total de 98 %** (20 min).
- Frontend: **89 pruebas pasan** y el `npm run build` completo termina sin errores.
- La pantalla se revisó a mano en local con las rutas confirmadas del 07-10-2026 y se vio correcta.
- Lighthouse el 22-10-2026: accesibilidad, buenas prácticas y SEO en 100, y W3C con 0 errores y 0 avisos (detalle en [`06 Calidad de la interfaz y pruebas de extremo a extremo`](06%20Calidad%20de%20la%20interfaz%20y%20pruebas%20de%20extremo%20a%20extremo%20V_1_0_0.md)).

Rendimiento en el equipo de desarrollo, con las franjas incluidas (150 pedidos, 15 vehículos):

| Medida | Resultado | Límite |
|---|---|---|
| Matrices | 1.3 s (0.85 s sin hora punta) | — |
| Generación, 10 corridas: mediana / percentil 95 / máximo | 12.8 s / 20.2 s / 21.1 s | 45 s (RN-015) |
| Re-optimización con presupuesto de 25 s, 3 semillas, total con reserva de guardado | 17.9 a 22.8 s | 30 s (RN-012) |

### 8.1 Medición en Render (20-10-2026, tras el Pull Request #56)

Mismo escenario y mismo script que la medición de HU-012 (`backend/tests_manual/medir_reoptimizacion_render.py`, local y no versionado): servicio gratuito de Render, 150 pedidos y 15 vehículos con 15 conductores (datos temporales ya borrados), 28 entregas registradas, 10 pedidos urgentes nuevos y congestión en Av. Ferrocarril (×3) y Av. Giráldez (×2), con la segunda matriz de hora punta.

| Medida | Resultado en Render | Límite |
|---|---|---|
| Generar rutas (150 pedidos, 15 vehículos) | 30.0 s; 14 rutas, 150 paradas, 0 sin cobertura | 45 s (RN-015) |
| Re-optimizar, 5 corridas (presupuesto de 25 s) | **22.2 s en el servidor y 24.0 a 24.2 s desde fuera** | 30 s (RN-012) |
| Desglose de la re-optimización | lectura ~1.9 s, matrices 13.0 a 13.6 s, motor 5.4 a 6.0 s (2 a 3 iteraciones), guardado 1.3 s | — |
| Mapa, primera petición (14 trazados, 106 KB, 2 126 puntos) | 9.3 s | — |
| Mapa, segunda petición (desde la caché) | 2.6 s | — |
| Congestión (43 KB) | 2.0 a 2.1 s | — |

Observaciones:

- **El margen de la re-optimización quedó ampliado:** 24.0 s medidos desde fuera, unos 6 s de holgura sobre el límite de 30 s (antes 29.0 s).
- **La segunda matriz tiene costo en Render:** las matrices pasaron de 9.2–9.6 s a 13.0–13.6 s (unos 4 s más, como se anticipó). El motor queda con 5.4 a 6.0 s y hace 2 a 3 iteraciones (antes 7 a 9). Como la re-optimización parte del plan vigente y aplica búsqueda local, el resultado nunca es peor, pero el ACO aporta poca mejora adicional en el plan gratuito. Mejoras posibles: reutilizar las matrices entre peticiones, resolver distancia y tiempo con una sola pasada de Dijkstra, o un plan con más CPU.
- **Cada petición cuesta unos 2 s de latencia base** (IMP-016): los 2.6 s del mapa desde la caché son casi todo latencia, por lo que el refresco cada 30 s es sostenible. La primera carga (9.3 s) se mitiga con el aviso en pantalla. La caché es por proceso: cuando Render duerme el servicio, la primera carga vuelve a tardar.
- **La generación quedó en 30.0 s** porque su presupuesto por defecto es de 30 s; con la segunda matriz el motor recibe unos 4 s menos que antes.

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: mapa de rutas con trazado por calles (HU-013), congestión por horas punta de RF-003, cambios en el motor, API, pantalla, pruebas y rendimiento local | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-20 | Se agrega la medición en Render del mapa, la generación y la re-optimización con hora punta, y el aviso de carga de la pantalla | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-22 | Se agregan el panel plegable del mapa, los resultados de Lighthouse y W3C y las 89 pruebas del frontend | Inciso Aguilar Elizabeth Antonela |
