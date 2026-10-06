# Tasks

## 1. Base de datos, dependencias y configuración

- [x] 1.1 Redactar el SQL de `rutas` (con `lote_id`), `ruta_pedidos` y `metricas_sostenibilidad`, el estado `CONFIRMADA`, los índices (`rutas(fecha_jornada, estado)`, `rutas(lote_id)`, `pedidos(estado, creado_en)`, `pedidos(prioridad)`, `pedidos(cliente_id)`), la política RLS permisiva y el `GRANT` a `app_backend` y `app_admin`; entregarlo a la usuaria para ejecutarlo en Supabase y verificar con una consulta que las tablas existen y que `app_backend` puede hacer `SELECT` sobre ellas
- [x] 1.2 Crear `docs/01 Inicio/11. Base de datos V_1_7_0.md` con las tablas, el estado, los índices y su historial de cambios, y actualizar el README; verificar que los enlaces abren la versión nueva
- [x] 1.3 Agregar `numpy` y `scipy` a `backend/requirements.txt` con tope superior de versión y verificar con `pip install -r requirements.txt` y `python -c "import scipy, numpy"`
- [x] 1.4 Agregar a `config.py` el depósito (-12.043632, -75.226373) como valor por defecto sobrescribible por `.env`, el factor de velocidad urbana (0.6), la hora de inicio de jornada (08:00), el tiempo de atención por parada (10 min) y el presupuesto de tiempo (30 s, máximo 40 s); verificar que el servidor arranca sin variables nuevas en el `.env`

## 2. Independencia de módulos (HT-08)

- [x] 2.1 Mover `clientes/zona.py` a `core/zona.py` y actualizar `clientes` y `pedidos`; verificar que `tests/test_clientes.py` y `tests/test_pedidos.py` siguen pasando
- [x] 2.2 Reemplazar en `pedidos` el uso de `clientes.repository` por una consulta propia de existencia del cliente; verificar con `test_pedidos.py` (registro con cliente inexistente devuelve 404)
- [x] 2.3 Crear `tests/test_arquitectura.py`, que analiza las importaciones con `ast` y falla si un módulo de negocio importa a otro (salvo `core` y `auditoria`) o si `algoritmo` importa FastAPI, SQLAlchemy u otro módulo del backend; verificar que pasa y que falla al introducir a propósito una importación prohibida

## 3. Red vial

- [x] 3.1 Escribir `backend/scripts/generar_grafo.py` (Overpass, sentidos únicos y rotondas, velocidad por tipo de vía, nombre de cada tramo, componente mayor) y generar `backend/data/huancayo_grafo.npz`; verificar que el archivo pesa menos de 1 MB y que el resumen impreso muestra cerca de 38 mil nodos y 84 mil tramos
- [x] 3.2 Implementar `red_vial/` (carga única del grafo, asignación al nodo más cercano con umbral de 500 m, matrices de distancia y tiempo por bloques de 25 fuentes y respaldo en línea recta × 1.35 que informa la fuente usada) y verificar con pruebas unitarias sobre un grafo sintético pequeño
- [x] 3.3 Probar sentidos únicos respetados, archivo ausente con respaldo, punto a más de 500 m con respaldo y avenida más rápida que calle residencial; verificar que `tests/test_red_vial.py` pasa
- [x] 3.4 Medir la matriz de 151 × 151 con el grafo real y verificar que tarda menos de 5 s y usa menos de 100 MB adicionales (prueba marcada `benchmark`)
- [x] 3.5 Crear `docs/03 Ejecución/Sprint 2/02 Implementación del motor de rutas V_1_0_0.md` con la sección de red vial (procedencia de los datos, cómo regenerar el grafo, velocidades y crédito "© OpenStreetMap contributors") y verificar que el comando documentado regenera el archivo

## 4. Núcleo del algoritmo

- [x] 4.1 Implementar `algoritmo/modelo.py` y `algoritmo/evaluacion.py` (costo ponderado y simulación del itinerario con espera, atención, descanso de 60 min cada 4 h y tope de 8 h); verificar con pruebas de itinerarios calculados a mano
- [x] 4.2 Implementar el emparejamiento vehículo-conductor (compatibilidad de categoría, licencia vigente en la fecha, disponibilidad y tabla opcional de restricción por placa) y verificar con pruebas de licencia vencida, categoría incompatible, sin tabla y con tabla
- [x] 4.3 Implementar la solución inicial voraz (express primero, capacidad, jornada) y verificar con pruebas de que ningún vehículo supera su capacidad y de que cada pedido aparece una sola vez o como sin cobertura
- [x] 4.4 Implementar el ACO tipo ACS con selección vectorizada, mejora local (reubicación y 2-opt) y parada por tiempo, iteraciones sin mejora o iteraciones máximas; verificar que nunca es peor que la solución voraz, que es reproducible con semilla y tope de iteraciones fijo y que respeta el presupuesto de tiempo con tolerancia de 1 s
- [x] 4.5 Implementar los pedidos sin cobertura con motivo (capacidad, falta de recursos, falta de tiempo) y sugerencias, incluido el caso sin vehículos; verificar con pruebas de cada motivo
- [x] 4.6 Crear el benchmark sintético de 150 pedidos y 15 vehículos (marca `benchmark`, percentil 95 sobre al menos 10 ejecuciones) y verificar que el tiempo total no supera 45 s en local; ejecutar además el mismo caso con 5, 10 y 15 minutos de atención por parada y registrar cuánto cambian la distancia, las emisiones y las entregas tardías
- [x] 4.7 Agregar al documento `02 Implementación del motor de rutas` la sección del algoritmo (modelo, parámetros, supuestos de licencia y de costo) y los resultados del benchmark local; verificar que las cifras coinciden con la salida del benchmark

## 5. Módulo de rutas (backend)

- [x] 5.1 Implementar `rutas/repository.py` con SQL parametrizado: lectura de pedidos pendientes, vehículos y conductores elegibles, escritura de rutas, paradas y métricas, y operaciones por lote; verificar con pruebas de integración contra la base real
- [x] 5.2 Implementar el servicio de generación (fecha no pasada, candado de una generación a la vez, lectura con `commit()` previo al cálculo, reaplicación del contexto RLS, reemplazo atómico de borradores con `pg_advisory_xact_lock`); verificar que una segunda solicitud simultánea devuelve 409 y que los borradores previos se reemplazan sin tocar rutas confirmadas
- [x] 5.3 Implementar confirmar (comprobación de pedidos aún PENDIENTE, rutas a CONFIRMADA y pedidos a ASIGNADO en una transacción) y descartar (rechazo si ya está confirmado); verificar el rechazo con pedido cancelado durante la revisión y con descarte de rutas confirmadas
- [x] 5.4 Implementar `rutas/router.py` y sus esquemas con los roles (generar, confirmar y descartar: ADMINISTRADOR; consultar: ADMINISTRADOR y OPERADOR), registrar `ruta_generada`, `ruta_confirmada` y `ruta_descartada` en la auditoría y registrar el router en `main.py`; verificar que Swagger muestra los endpoints y que un CONDUCTOR recibe 403
- [x] 5.5 Escribir `tests/test_rutas.py` con los escenarios de `route-planning` y `route-optimization` contra la base real (generación exitosa, fecha pasada, sin vehículos, sin cobertura por peso, regeneración, confirmación, pedido cancelado, descarte, consulta por rol, auditoría sin DNI) y verificar que la suite pasa con limpieza de datos
- [x] 5.6 Actualizar `docs/01 Inicio/12. Modelo C4` (nueva versión) con los módulos `rutas`, `red_vial` y `algoritmo`; verificar que el diagrama de nivel 3 muestra la relación router → servicio → repositorio → motor

## 6. Escalabilidad de la API (HT-08)

- [ ] 6.1 Paginar `GET /api/pedidos` (`limite` 50 por defecto y 200 máximo, `desplazamiento`, `total` en la respuesta) y verificar con pruebas de página por defecto, límite excesivo (rechazo) y filtros combinados
- [ ] 6.2 Comprobar con `EXPLAIN` que las consultas de listado y de pedidos pendientes por fecha usan los índices nuevos; verificar que el plan muestra un recorrido por índice con 1,000 pedidos
- [ ] 6.3 Escribir la prueba de carga (marca `carga`) que inserta 1,000 pedidos, mide el percentil 95 del listado, el registro y la cancelación y limpia después; verificar que es ≤ 2 s y documentar el resultado en el documento de implementación

## 7. Frontend

- [ ] 7.1 Adaptar `PedidosPage` a la respuesta paginada con "Cargar más" y verificar con `npm run build` y una prueba manual de más de 50 pedidos
- [ ] 7.2 Crear `RutasPage` (selector de fecha, generar con indicador de progreso, aviso de borrador, métricas, paradas por ruta, pedidos sin cobertura con motivo, confirmar y descartar con confirmación) con ayudas "i", adaptable a pantallas angostas, y registrarla en el menú y las rutas (Administrador completo, Operador solo consulta); verificar con `npm run build` y revisión a 360 px
- [ ] 7.3 Agregar pruebas de Vitest de `RutasPage` (el Administrador ve confirmar y descartar, el Operador no, y se muestra el aviso de borrador) y verificar que `npx vitest run` pasa

## 8. Integración y cierre

- [ ] 8.1 Agregar `rutas`, `red_vial` y `algoritmo` a `--cov` en `pytest.ini` y verificar que `pytest tests` pasa con cobertura total de 80 % o más
- [ ] 8.2 Desplegar en Render y medir allí el benchmark de 150 pedidos y 15 vehículos (percentil 95) y la memoria del servicio durante una generación; registrar los resultados y verificar que el tiempo total no supera 45 s
- [ ] 8.3 Ejecutar Bandit, `pip-audit` y `npm audit` y verificar que no hay vulnerabilidades críticas
- [ ] 8.4 Recorrer de extremo a extremo el flujo con datos reales (generar, revisar, regenerar, confirmar y descartar) como Administrador y como Operador y verificar cada escenario de las specs
- [ ] 8.5 Actualizar el plan de ejecución del Sprint 2 (HU-011, HT-07 y HT-08), el informe de estado y el README, y preparar los commits y el Pull Request; verificar que los enlaces del README abren las versiones nuevas
