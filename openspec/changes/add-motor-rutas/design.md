# Design

## Context

Estado actual (ver `proposal.md` para la motivación): el backend de FastAPI está organizado por características (`auth`, `flota`, `clientes`, `pedidos`, `conductores`, `auditoria`), con patrón Repository y SQL parametrizado; las tablas organizacionales llevan una política RLS permisiva y el control de acceso real lo aplica `requiere_rol`. Los repositorios no hacen `commit()`: el único commit ocurre al final de la petición en `get_db_con_rls`.

Restricciones que condicionan el diseño:

- **Despliegue en Render gratuito**: 512 MB de RAM, 0.1 de CPU y disco efímero. El servidor FastAPI en reposo usa unos 73 MB.
- **Una prueba de concepto medida** (descarga de OpenStreetMap, grafo y matriz con `scipy`): 38,272 nodos y 84,058 tramos dirigidos; archivo de 0.73 MB; matriz de 151 × 151 en 0.44 s de CPU; pico de memoria de +47 MB; la distancia por calles resultó 1.38 veces la línea recta de media (mediana 1.30); sin pares inalcanzables.
- **Datos de entrada ya existentes**: `pedidos` (peso, prioridad, ventana, coordenadas), `vehiculos` (capacidad, consumo, factor de CO₂, estado), `conductores` (categoría de licencia, vencimiento, horario, disponibilidad) y el depósito (parque industrial: -12.043632, -75.226373).
- **Dependencias cruzadas actuales** que contradicen HT-08: `pedidos` importa `clientes.repository` y `clientes.zona`.
- La norma de tránsito citada en los requisitos (DS 033-2001-MTC) no define una tabla de restricción por placa; RN-004 queda como parámetro configurable.

## Goals / Non-Goals

**Goals:**
- Generar rutas válidas por fecha de jornada en ≤ 45 s para 150 pedidos y 15 vehículos, cumpliendo capacidad, jornada, descanso y ventanas con penalización.
- Núcleo del algoritmo puro y probable sin base de datos, para poder compararlo con un GA en una iteración posterior.
- Flujo borrador → confirmar con persistencia de rutas, paradas y métricas de sostenibilidad.
- Cumplir HT-08: módulos independientes, paginación e índices, y prueba de carga con 1,000 pedidos.

**Non-Goals:**
- Congestión por horas punta en Av. Ferrocarril, Av. Giráldez y Calle Real, y re-optimización ante incidentes (HU-012): Sprint 3. El grafo guarda desde ahora el nombre de cada tramo para habilitarlo.
- Mapa interactivo (HU-013) y vista del conductor (HU-014).
- Algoritmo genético, multi-depósito, recogidas, restricciones de volumen, tiempos de viaje dependientes de la hora y foto del conductor (Cloudinary).
- Interfaz para editar manualmente las rutas o los pesos de la función objetivo.

## Decisions

### D1. Distancias por un grafo propio de OpenStreetMap, con scipy

Un script (`backend/scripts/generar_grafo.py`) descarga con Overpass las vías transitables de la zona urbana (caja -12.12 a -11.99 de latitud y -75.27 a -75.17 de longitud), arma el grafo dirigido (sentidos únicos y rotondas), calcula la longitud de cada tramo y su tiempo con la velocidad base por tipo de vía y guarda `backend/data/huancayo_grafo.npz` (arreglos `u`, `v`, `dist`, `seg`, `coords` y el nombre de cada tramo). En ejecución, `red_vial/` carga el archivo una vez, asigna cada punto al nodo más cercano de la **componente fuertemente conexa mayor** con un árbol KD y calcula matrices con `scipy.sparse.csgraph.dijkstra` **por bloques de 25 fuentes**.

- Velocidades base: calles y jirones 40 km/h, avenidas 60 km/h, residenciales 30, servicio 20 (DS 033-2001-MTC art. 162), multiplicadas por un factor de velocidad urbana de **0.6** (configurable; supuesto a calibrar) para reflejar tráfico y paradas.
- La matriz de distancias y la de tiempos se calculan **de forma independiente** (camino más corto por distancia y por tiempo). Es una simplificación: ambos caminos pueden diferir, pero evita guardar predecesores y es suficiente para el optimizador.
- Si un punto queda a más de 500 m de la red, o el archivo no carga, se usa línea recta × 1.35 y el resultado lo informa.

**Alternativas descartadas:** línea recta × 1.35 como solución principal (menos exacta, no modela avenidas); OpenRouteService (cuotas, clave, matrices limitadas a unos 59 × 59 puntos por petición, dependencia de red durante una operación con tope de 45 s); OSRM público (solo demostración); `osmnx` (arrastra librerías geográficas demasiado pesadas para 512 MB); servidor de rutas propio (excede el plan gratuito).

### D2. Núcleo del algoritmo: ACO con solución voraz y mejora local

`algoritmo/` es Python puro con `numpy`, sin importar FastAPI, SQLAlchemy ni ningún otro módulo del backend. Recibe un `Problema` (matrices, pedidos, "pares vehículo-conductor", parámetros) y devuelve una `Solucion`.

1. **Pares vehículo-conductor**: se forman antes de optimizar con un emparejamiento voraz por compatibilidad de categoría (supuesto: `A-*` conducen CAMIONETA y FURGON; `B-IIa` y `B-IIb`, MOTO), disponibilidad y vigencia de licencia. Cada par fija capacidad, consumo, factor de CO₂ y la ventana horaria del conductor.
2. **Solución inicial voraz** (vecino más cercano con factibilidad, express primero): garantiza una respuesta válida y es la línea base de comparación.
3. **ACO tipo ACS**: 20 hormigas (o N si hay menos pedidos), α = 1, β = 3, evaporación 0.1, regla pseudoaleatoria proporcional con q0 = 0.9, depósito elitista de la mejor solución; la visibilidad es el inverso del costo incremental (distancia + penalización de ventana estimada). La selección del siguiente pedido se **vectoriza con numpy**, y se comprueba la factibilidad (capacidad, jornada, ventana del conductor) en cada paso.
4. **Mejora local** de la mejor solución de cada iteración: reubicación y 2-opt dentro y entre rutas.
5. **Parada**: presupuesto de tiempo (30 s por defecto, tope 40 s), 50 iteraciones sin mejora, o 500 iteraciones.
6. **Itinerario** de cada ruta: salida a `max(08:00, inicio del conductor)`, 10 minutos fijos de atención por parada (decisión confirmada; supuesto sin datos reales de Andina, con prueba de sensibilidad a 5 y 15 minutos), espera si se llega antes de la ventana y descanso de 60 minutos al acumular 4 horas de trabajo continuo; la ruta es inválida si supera 8 horas o el horario del conductor.

**Costo** = 1.0 · km + 1.0 · litros + 2.0 · kg de CO₂ + 0.5 · Σ (ponderación de prioridad · minutos de retraso), con ponderaciones EXPRESS 5, ESTANDAR 1 y ECONOMICO 0.5. Son valores iniciales, configurables y por calibrar con el benchmark. Los EXPRESS se colocan primero dentro de cada ruta. La reproducibilidad se obtiene con una semilla y un tope de iteraciones fijo.

**Alternativas descartadas:** GA como principal (el stack define ACO como principal y GA como mejora posterior); OR-Tools (excelente, pero el proyecto exige un metaheurístico propio y explicable en la sustentación); terminar por número de iteraciones (en 0.1 de CPU no sería predecible).

### D3. Persistencia, estados y concurrencia

Tablas `rutas` (más `lote_id`), `ruta_pedidos` y `metricas_sostenibilidad`, con RLS permisiva y `GRANT` a `app_backend` y `app_admin`, como las demás tablas organizacionales; `rutas.estado` incorpora `CONFIRMADA`. Índices: `rutas(fecha_jornada, estado)`, `rutas(lote_id)`, `pedidos(estado, creado_en)`, `pedidos(prioridad)` y `pedidos(cliente_id)`.

- **Regenerar**: dentro de una sola transacción, con `pg_advisory_xact_lock` por fecha, se eliminan los borradores PLANIFICADA de esa fecha y se insertan los nuevos.
- **Confirmar**: transacción única que comprueba que todos los pedidos del lote sigan en PENDIENTE (si no, 409 con la lista), pasa las rutas a CONFIRMADA y los pedidos a ASIGNADO.
- **Una generación a la vez** por proceso: un candado en memoria; una segunda solicitud recibe 409.
- **Transacción corta**: el cálculo puede durar hasta 40 s, así que el servicio lee los datos, hace `commit()` para liberar la conexión, calcula sin transacción abierta y reabre el contexto de RLS (`reaplicar_contexto_rls` en `core`) para escribir. Es una excepción documentada a la convención de "un solo commit al final", aceptable porque las tablas involucradas tienen política permisiva y no dependen de `app.usuario_actual_id`.
- Auditoría: `ruta_generada`, `ruta_confirmada` y `ruta_descartada`, con el id del lote y sin datos personales.

### D4. API

- `POST /api/rutas/generar` `{fecha_jornada, tiempo_max_s?}` → 201 con `lote_id`, rutas (vehículo, conductor, métricas y paradas ordenadas con hora estimada), `sin_cobertura` (pedido, motivo, sugerencia), `fuente_distancias`, `comparativa_base` y `tiempo_ejecucion_s`. Solo ADMINISTRADOR.
- `GET /api/rutas?fecha=` y `GET /api/rutas/{ruta_id}`: ADMINISTRADOR y OPERADOR.
- `POST /api/rutas/lotes/{lote_id}/confirmar` y `DELETE /api/rutas/lotes/{lote_id}`: solo ADMINISTRADOR.
- `GET /api/pedidos` pasa a `{items, total, limite, desplazamiento}` con límite por defecto de 50 y máximo de 200.

### D5. Independencia de módulos (HT-08)

La zona de cobertura (`clientes/zona.py`) pasa a `core/zona.py`; `pedidos` comprueba la existencia del cliente con su propia consulta SQL en lugar de importar `clientes.repository`. Los únicos módulos compartidos son `core` y `auditoria`. Un test analiza las importaciones con `ast` y falla si aparece una dependencia prohibida.

### D6. Frontend

Una pantalla `RutasPage` (Administrador genera, confirma y descarta; Operador consulta): selector de fecha, botón de generar con indicador de progreso (hasta 40 s), aviso visible de "borrador sin confirmar", métricas, paradas por ruta, pedidos sin cobertura con su motivo, y confirmar o descartar con confirmación. El listado de pedidos se adapta a la paginación con "Cargar más". Todo adaptable a pantallas angostas y con el crédito de OpenStreetMap en la documentación.

## Risks / Trade-offs

- **[CPU de Render gratuito (0.1)]** → el ACO hará menos iteraciones que en local y la solución será menos pulida. Se mitiga terminando por tiempo, midiendo el benchmark en Render al final del cambio y dejando el presupuesto de tiempo configurable.
- **[Calidad de los datos de OpenStreetMap]** (solo 8 % de las vías con sentido único marcado, 4 % con límite de velocidad) → un sentido único faltante podría proponer un giro prohibido. Se mitiga con velocidades por tipo de vía, verificación visual cuando exista el mapa (Sprint 3) y un archivo de ajustes manuales futuro.
- **[Dependencia nueva: numpy y scipy, ~190 MB instalados]** → se fijan con tope superior de versión (acción de la retrospectiva del Sprint 1) y se mide la memoria en Render.
- **[Solicitud larga de hasta 40 s]** → un proxy o el navegador podrían cortarla. Se mitiga con el tope de 40 s, el indicador de progreso y el candado de una generación a la vez; si Render corta conexiones largas, se evaluará convertirla en tarea asíncrona (fuera de este cambio).
- **[Pesos y parámetros del ACO son supuestos iniciales]** → se calibran con el benchmark y quedan configurables; no son requisitos normativos.
- **[Compatibilidad licencia-vehículo es un supuesto]** → documentado; se ajusta si el docente indica otra tabla.
- **[Cambio de contrato de `GET /api/pedidos`]** → el frontend se adapta en este mismo cambio; no hay otros consumidores.
- **[Matrices independientes de distancia y tiempo]** → posible leve inconsistencia entre ambos caminos; aceptable para el MVP.

## Migration Plan

1. Ejecutar manualmente en Supabase el SQL de tablas, índices, política RLS, `GRANT` y estado `CONFIRMADA` (documentado en `11. Base de datos`, versión nueva).
2. Generar el grafo con el script y versionar `data/huancayo_grafo.npz` (≈ 0.7 MB).
3. Agregar `numpy` y `scipy` a `requirements.txt`; el depósito va como valor por defecto en `config.py`, así que no hay variables nuevas en Render.
4. Desplegar el backend, medir el benchmark de 150 pedidos y 15 vehículos en Render y registrar los resultados en el documento de pruebas.
5. **Reversa**: quitar el router `rutas` de `main.py`; las tablas nuevas pueden quedar sin uso sin afectar al resto del sistema. El cambio de paginación de pedidos se revierte junto con el frontend.

## Open Questions

- Los valores finales de pesos de la función objetivo y de los parámetros del ACO se fijarán con el benchmark; no cambian las specs ni las tareas.
- Si convendrá guardar un archivo de ajustes manuales sobre el grafo (sentidos únicos corregidos) se decidirá cuando exista el mapa de rutas.
