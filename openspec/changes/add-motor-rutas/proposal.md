# Proposal

## Why

RouteZero ya registra pedidos, vehículos, conductores y clientes (Sprints 1 y 2), pero todavía no cumple su objetivo central: **generar rutas de reparto optimizadas** que minimicen distancia, combustible, emisiones de CO₂ y entregas tardías para Andina Reparto S.A.C. en Huancayo (RF-003, HU-011, RN-015). Sin el motor de optimización no hay rutas que mostrar en el mapa (Sprint 3), ni indicadores de sostenibilidad (Sprint 4), y el sprint en curso (Personas y Algoritmo ACO) compromete 28 SP en este frente (HU-011, HT-07, HT-08).

Además, se decidió calcular las distancias sobre **calles reales de Huancayo** (datos de OpenStreetMap) en lugar de una aproximación en línea recta, porque una prueba de concepto mostró que es viable, gratuito y cabe en el plan gratuito de Render: grafo de 0.73 MB, matriz de 151 × 151 puntos en 0.44 s de CPU y pico de memoria de unos 47 MB.

## What Changes

- **Red vial propia de Huancayo**: un script de una sola vez descarga las calles de OpenStreetMap y genera un archivo de grafo versionado en el repositorio; en tiempo de ejecución se calculan matrices de distancia y tiempo entre pedidos y depósito por calles reales (sentidos únicos, velocidad por tipo de vía). Respaldo: distancia en línea recta × 1.35.
- **Motor de optimización ACO (VRPTW + Green VRP)**: módulo de Python puro, sin dependencia de la base de datos ni de FastAPI, con solución inicial voraz, mejora local y límite de tiempo (≤ 45 s para 150 pedidos y 15 vehículos).
- **Módulo `rutas/`**: generación de rutas por fecha de jornada, con flujo **borrador → confirmar**: generar deja rutas `PLANIFICADA`; el Administrador revisa, regenera, descarta o confirma (`CONFIRMADA`, con pedidos pasando a `ASIGNADO`). Informa los pedidos sin cobertura con motivo y sugerencias.
- **Persistencia**: tablas `rutas`, `ruta_pedidos` y `metricas_sostenibilidad` (ya diseñadas en `11. Base de datos`), con un identificador de lote y el nuevo estado `CONFIRMADA`.
- **Pantalla "Rutas"** (mínima, sin mapa): generar, revisar métricas y paradas, confirmar o descartar.
- **Escalabilidad (HT-08)**: índices SQL, paginación del listado de pedidos y prueba de carga con 1,000 pedidos.
- **Dependencias nuevas** en el backend: `numpy` y `scipy`, con tope superior de versión.
- **BREAKING (menor)**: `GET /api/pedidos` pasa a estar paginado (límite por defecto); el frontend actual se adapta en este mismo cambio.

## Capabilities

### New Capabilities
- `road-network`: red vial de Huancayo derivada de OpenStreetMap; matrices de distancia y tiempo por calles reales, con respaldo en línea recta y atribución de la fuente.
- `route-optimization`: comportamiento del motor de optimización: restricciones duras y blandas, función objetivo, prioridad express, asignación de conductores y vehículos compatibles, límite de tiempo y mejora sobre la solución voraz.
- `route-planning`: generación, consulta, confirmación y descarte de rutas por jornada, con borrador antes de confirmar, pedidos sin cobertura y control de acceso por rol.
- `api-scalability`: respuesta de la API dentro de 2 s con 1,000 pedidos diarios, con listados paginados.

### Modified Capabilities
<!-- Ninguna: no existen specs previas de pedidos, flota ni conductores; sus requisitos viven en los documentos de la fase de Inicio. -->

## Impact

- **Backend**: nuevos paquetes `algoritmo/` (núcleo puro), `red_vial/` (grafo y matrices) y `rutas/` (router, servicio, repositorio); `main.py` registra el router; `config.py` incorpora el depósito (-12.043632, -75.226373) como valor por defecto; `requirements.txt` agrega `numpy` y `scipy`; un script `scripts/generar_grafo.py` y el archivo de datos `data/huancayo_grafo.npz`.
- **Base de datos** (Supabase, a ejecutar manualmente): tablas nuevas con RLS y `GRANT`, estado `CONFIRMADA`, índices de pedidos y rutas. Nueva versión de `11. Base de datos`.
- **Frontend**: pantalla Rutas y ajuste del listado de pedidos paginado.
- **Documentación**: `12. Modelo C4` (módulo de rutas), plan de ejecución del Sprint 2, plan y resultados de pruebas del motor; crédito "© OpenStreetMap contributors".
- **Despliegue**: Render gratuito (512 MB de RAM, 0.1 de CPU): el motor termina por tiempo, no por iteraciones, y se mide allí al final del cambio.
- **Fuera de este cambio** (Sprint 3): congestión en horas punta sobre Av. Ferrocarril, Av. Giráldez y Calle Real, re-optimización ante incidentes (HU-012), mapa interactivo (HU-013) y vista del conductor (HU-014).
