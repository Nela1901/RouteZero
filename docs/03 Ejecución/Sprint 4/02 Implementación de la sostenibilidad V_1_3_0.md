# 02 Implementación de la sostenibilidad (dashboard, plan de compensación y reporte PDF)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22 oct – 13 nov 2026) |
| **Historias cubiertas** | HU-015 (dashboard de indicadores), HU-017 (plan de compensación de carbono), HU-016 (reporte PDF), HT-12 (pruebas del reporte) y HT-11 (optimización de consultas) |
| **Fecha de corte** | 2026-10-23 |
| **Versión** | 1.3.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Alcance

Este documento describe lo implementado en la épica EP-07 (Sostenibilidad). El estado de cada ítem está en el [`01 Sprint 4 Plan de ejecución y estado`](01%20Sprint%204%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_4_0.md).

## 2. Módulo `sostenibilidad` del backend

Un módulo nuevo, `backend/src/sostenibilidad/`, con la misma organización por características del resto del backend (router → servicio → repositorio), más `reporte.py`, que dibuja el PDF. **No importa código de otros módulos de negocio**: consulta las tablas `rutas`, `ruta_pedidos`, `pedidos`, `vehiculos`, `conductores` y `metricas_sostenibilidad` con su propio SQL parametrizado, igual que `flota` consulta `rutas`. La prueba de arquitectura (`test_arquitectura.py`) lo vigila.

| Endpoint | Rol | Respuesta |
|---|---|---|
| `GET /api/sostenibilidad/dashboard?desde=&hasta=` | ADMINISTRADOR | Totales del periodo (rutas, distancia, CO₂, combustible, combustible ahorrado, ahorro en soles, cumplimiento de ventanas), entregas realizadas, pendientes y fallidas, y serie de emisiones por día |
| `GET /api/sostenibilidad/compensacion?desde=&hasta=` | ADMINISTRADOR | CO₂ del periodo, árboles necesarios, comparación del mes con la meta mensual, acciones de reducción y alianzas de reforestación a explorar |
| `GET /api/sostenibilidad/reporte?desde=&hasta=` | ADMINISTRADOR | Reporte en PDF (`application/pdf`, descarga con nombre `reporte-sostenibilidad-<desde>-<hasta>.pdf`); responde 404 con un mensaje si el periodo no tiene jornadas |

- **Periodo.** Sin fechas se toma el mes en curso hasta hoy (hora de Perú). No puede ser invertido ni abarcar un año o más: en esos casos responde 422.
- **Qué cuenta.** Las rutas `CONFIRMADA`, `EN_EJECUCION` y `COMPLETADA` cuya fecha de jornada cae en el periodo. Un borrador (`PLANIFICADA`) o una ruta cancelada no es una jornada realizada y no suma. Las entregas excluyen los pedidos cancelados.
- **Cálculos.**
  - Emisiones y distancia: suma de `metricas_sostenibilidad` (la emisión de cada ruta ya es distancia × factor de emisión del vehículo, RN-009).
  - Cumplimiento de ventanas: promedio de las rutas ponderado por su número de paradas.
  - Ahorro económico: combustible ahorrado × precio del litro. Se calcula al consultar y no se guarda, porque el precio es un supuesto ajustable; la columna `ahorro_soles` sigue existiendo en la tabla, pero no se usa.
  - Árboles necesarios (RN-011): emisiones del periodo ÷ kilogramos de CO₂ que absorbe un árbol al año, redondeado hacia arriba.
  - Meta mensual (RN-010): se compara el mes de la fecha final, desde su día 1, con la meta; si la supera, se devuelve la alerta y tres acciones de reducción.
- **Sin datos.** Con el periodo vacío el dashboard devuelve todo en cero y el mensaje «No hay jornadas operativas registradas en el periodo seleccionado.», el plan pide ejecutar al menos una jornada operativa y no propone alianzas, y el reporte responde 404 con «No hay datos suficientes para generar el reporte en el periodo seleccionado. Seleccione otro periodo.», sin generar un PDF vacío.
- **Permisos.** Solo el administrador (RN-014); el operador y el conductor reciben 403.

## 3. Supuestos configurables

No hay datos reales de la empresa ficticia, así que estos valores son **supuestos declarados** y se ajustan con una variable de entorno en mayúsculas, sin tocar el código (`backend/src/core/config.py`):

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `PRECIO_COMBUSTIBLE_SOLES_L` | 4.50 (soles por litro) | Convierte el combustible ahorrado y el gastado en soles |
| `META_MENSUAL_CO2_KG` | 800 (kg al mes) | Umbral de la alerta de la RN-010 |
| `KG_CO2_POR_ARBOL_ANIO` | 22 (kg por árbol al año) | Cantidad de árboles de la RN-011; con este valor una tonelada pide unos 46 árboles |

Las **alianzas de reforestación** que muestra el plan son propuestas de tipos de organización a contactar (Gobierno Regional de Junín y SERFOR, comunidades campesinas de la provincia de Huancayo, universidades e institutos). **No hay convenios firmados** con ninguna institución y la pantalla y el PDF lo dicen.

## 4. Reporte en PDF (HU-016)

- **Contenido.** Encabezado con el periodo y la fecha de generación, y cinco secciones: resumen del periodo, emisiones de CO₂ por ruta, costo del ciclo de vida de la flota, metas de sostenibilidad y compensación, y supuestos y notas. Lleva numeración de páginas.
- **Reporte parcial.** Si el periodo incluye rutas todavía confirmadas o en ejecución, el PDF abre con el aviso «REPORTE PARCIAL: … las cifras corresponden a los datos disponibles hasta el momento» (escenario alternativo del requisito RF-006).
- **Costo del ciclo de vida de la flota.** El vehículo ahora guarda el **precio de compra** y la **vida útil en años** (opcionales). El costo del periodo es `precio ÷ (vida útil × 365) × días del periodo` más el combustible gastado por el precio del litro. Un vehículo sin esos datos aparece como «sin dato» y **no suma** al total; el PDF indica cuántos faltan. Se completan en el módulo de Flota, cuyo formulario y detalle ya traen los dos campos.
- **Límite de tamaño.** Lista como máximo las 300 rutas más recientes del periodo; si hay más, lo dice y las incluye en los totales.
- **Generación.** Biblioteca `fpdf2` (Python puro, ligera para el plan gratuito de Render) con las fuentes básicas del PDF: hay tildes y «ñ», pero «CO₂» se escribe «CO2» porque esas fuentes no tienen el subíndice. Un texto fuera de Latin-1 se reemplaza en vez de romper el documento. En esta máquina un reporte de 300 rutas y 15 vehículos se dibuja en 0.4 s y pesa 21 KB.
- **Auditoría.** Cada descarga queda registrada como `reporte_generado` en `logs_auditoria`.
- **Descarga en la pantalla.** El botón «Descargar reporte PDF» de la pantalla Sostenibilidad pide el periodo elegido con la sesión del usuario, guarda el archivo y muestra el aviso de la API si no hay datos.

## 5. Pantalla Sostenibilidad del frontend

- Ruta `/app/sostenibilidad`, solo visible para el administrador (el operador no la ve en el menú y, si escribe la dirección, vuelve al mapa).
- Filtro de periodo con atajos «Hoy», «Últimos 7 días» y «Este mes», más fechas «Desde» y «Hasta». Por defecto, el mes en curso.
- Cinco indicadores con una ayuda que explica cómo se calcula cada uno, el resumen de jornadas y entregas, el gráfico de emisiones por día (con el valor en texto), el plan de compensación con la barra de la meta mensual y el botón del reporte.
- Cuando el mes supera la meta se muestra una alerta con las acciones sugeridas; cuando no hay datos, un aviso en lugar de cifras inventadas.
- Se adapta al ancho del celular sin desplazamiento horizontal. La pantalla consulta el dashboard y el plan a la vez, con dos peticiones.

## 6. Optimización de consultas (HT-11, RNF-011)

Con las tablas casi vacías de desarrollo, PostgreSQL recorre todo y cualquier consulta parece rápida; por eso se escribió `backend/scripts/auditar_consultas.py`. El script carga, **dentro de una transacción que siempre se deshace**, un volumen parecido al de seis meses de operación (2 700 rutas, 16 200 pedidos entregados y 150 pendientes), actualiza las estadísticas y mide 17 consultas críticas con `EXPLAIN (ANALYZE)`: tiempo en el servidor (mejor de 3 corridas, sin latencia de red), recorridos completos de tablas grandes y, con esos recorridos desactivados, qué índice podría resolver la consulta. Sale con error si alguna pasa de 500 ms o recorre una tabla grande sin índice utilizable.

Resultados del 23-10-2026:

| Consulta | Tiempo en el servidor |
|---|---|
| Generación: pedidos pendientes, vehículos disponibles y conductores elegibles | 0.1 a 0.2 ms |
| Rutas activas de la fecha (re-optimizar), listado de rutas de una fecha y ruta del conductor | 0.1 a 0.3 ms |
| Paradas de las rutas de un día | 6.3 ms |
| Listado de pedidos por estado | 0.2 ms |
| **Listado de pedidos sin filtro (antes del índice)** | **7.0 ms** (ordenaba todos los pedidos) |
| **Listado de pedidos sin filtro (con `idx_pedidos_creado`)** | **0.1 ms** |
| **Dashboard: totales de 30 días (antes del cambio)** | **6.6 ms** (contaba las paradas de todas las rutas del historial) |
| **Dashboard: totales de 30 días (contando solo las del periodo)** | **3.1 ms** |
| Dashboard: emisiones por día y costo de la flota | 0.9 y 1.1 ms |
| Dashboard: entregas | 10 a 42 ms (PostgreSQL alterna entre dos planes según las estadísticas del momento) |
| **Reporte: rutas del periodo (antes del cambio)** | **6.9 ms** |
| **Reporte: rutas del periodo (contando solo las del periodo)** | **2.5 ms** |
| Auditoría por módulo (incluido uno poco frecuente), sesiones activas y renovación de sesión | 0.0 a 0.1 ms |

- **Conclusión.** Las 17 consultas quedan en 42 ms o menos en el servidor, muy por debajo del umbral de 500 ms, y ninguna recorre una tabla grande sin tener un índice que la resuelva. Los índices que ya existían cubren el resto.
- **Dos mejoras reales.** (1) El índice `idx_pedidos_creado (creado_en DESC, pedido_id)` para el listado de pedidos sin filtro de estado (migración `backend/scripts/migracion_indices_ht11.sql`). (2) El dashboard y el reporte contaban las paradas de todas las rutas del historial aunque se pidiera un solo mes; ahora un `JOIN LATERAL` cuenta solo las del periodo, y el costo deja de crecer con el historial.
- **Límite.** El rol `app_admin` no es dueño de las tablas y no puede crear índices; las migraciones se ejecutan a mano en Supabase.
- **Lo que no se midió.** La latencia de red a Supabase: en Render cada petición cuesta unos 2 s (IMP-016), que no depende de los índices.

## 7. Pruebas y resultados

Mediciones del 23-10-2026, en esta máquina y con la base real:

| Prueba | Resultado |
|---|---|
| Backend: `test_sostenibilidad.py` (contra la base real) | 14 pruebas: periodo por defecto e inválido, borrador que no cuenta, suma de métricas contra la base, relación entre emisiones y factores de emisión, ahorro en soles, entregas y pedidos cancelados, ceros y mensaje, árboles y meta, permisos por rol |
| Backend: `test_reporte_pdf.py` (HT-12) | 15 pruebas: PDF válido con sus secciones y cifras leídas de vuelta con `pypdf`, aviso de reporte parcial, vehículos sin datos, meta cumplida y superada, varias páginas y rutas omitidas, texto fuera de Latin-1, 404 sin datos y sin PDF vacío, costo del ciclo de vida (200 soles de depreciación en 10 días de una camioneta de 73 000 soles a 10 años), descarga por la API con su registro de auditoría, permisos y periodo inválido |
| Backend: `test_flota.py` | 2 pruebas nuevas: precio de compra y vida útil al registrar y editar, y validación de rangos |
| Prueba de arquitectura | Pasa con el módulo nuevo |
| Suite completa del backend | 359 pruebas pasan en 26 min contra la base real; cobertura total 98 %; el módulo `sostenibilidad` tiene 100 % (se agregó a `pytest.ini` para medirlo) |
| Análisis estático | Bandit sin hallazgos en el módulo; `pip-audit` sin vulnerabilidades con `fpdf2` y `pypdf` |
| Vitest | 99 pruebas pasan en total: 8 de la pantalla Sostenibilidad y 2 nuevas de Flota |
| Playwright de escritorio (`sostenibilidad.spec.ts`) | 6 pruebas: indicadores y plan con alerta, atajo «Hoy», periodo sin datos, descarga del reporte con el nombre del archivo, aviso sin datos y el operador sin acceso |
| Playwright en celular | 1 prueba nueva: sin desplazamiento horizontal |
| Playwright completo | 26 pruebas pasan, de escritorio y celular |
| Lighthouse (Sostenibilidad, con el botón del reporte) | Escritorio: rendimiento 99; móvil: rendimiento 95; accesibilidad, buenas prácticas y SEO en 100 en ambos |
| Validador W3C (Sostenibilidad) | 0 errores y 0 avisos |
| `npm audit` (nivel alto) | 0 vulnerabilidades |

## 8. Medición en Render (producción)

Medido el 23-10-2026 contra `https://routezero-7k7j.onrender.com` (plan gratuito, CPU 0.1) con la cuenta administradora y datos temporales marcados que se borraron al terminar (`backend/tests_manual/medir_sostenibilidad_render.py`): un mes de operación (30 días × 15 rutas con 6 paradas, 450 rutas y 2 700 paradas), en fechas lejanas para no mezclarse con la operación real. Cuatro peticiones por caso.

| Petición | Estado | Mediana | Mejor | Peor | Tamaño |
|---|---|---|---|---|---|
| Dashboard, 30 días (450 rutas) | 200 | 2.4 s | 2.4 s | 2.6 s | 3 KB |
| Dashboard, 1 día (15 rutas) | 200 | 2.3 s | 2.3 s | 2.4 s | < 1 KB |
| Plan de compensación, 30 días | 200 | 2.3 s | 2.3 s | 2.4 s | 1 KB |
| Reporte PDF, 30 días (300 rutas listadas) | 200 (`application/pdf`) | 7.5 s | 7.4 s | 7.7 s | 23 KB |
| Reporte PDF, 1 día (15 rutas) | 200 (`application/pdf`) | 3.3 s | 3.3 s | 3.4 s | 5 KB |
| Reporte sin datos | 404 | 2.2 s | 2.2 s | 2.2 s | < 1 KB |

- **El dashboard y el plan** cuestan lo mismo que cualquier petición del sistema en Render, unos 2.3 s: casi todo es la latencia de red hacia la base (IMP-016), no las consultas, que en el servidor tardan 3 ms. Pasar de 15 a 450 rutas casi no cambia el tiempo (2.3 s → 2.4 s).
- **El reporte** suma el dibujo del PDF. Con el máximo que lista (300 rutas) toma 7.5 s; un reporte de un día, 3.3 s. En esta máquina el dibujo del PDF más grande toma 0.4 s, así que en Render la CPU de 0.1 lo multiplica por unas 12. Es aceptable para una descarga que el administrador pide a mano, y la pantalla muestra «Generando reporte…» mientras tanto.
- Los datos temporales se borraron (0 vehículos, 0 conductores y 0 pedidos de la medición al terminar).

## 9. Limitaciones conocidas

- Tras una re-optimización, las métricas de la ruta cubren solo el tramo restante (ver [`02 Implementación de la re-optimización`](../Sprint%203/02%20Implementaci%C3%B3n%20de%20la%20re-optimizaci%C3%B3n%20V_1_3_0.md)); el dashboard y el reporte pueden quedar por debajo de lo recorrido en las rutas re-optimizadas del periodo.
- El combustible ahorrado se mide frente a la solución inicial del optimizador, no frente a una operación real sin optimizar.
- Los tres supuestos de la sección 3 deben validarse con Andina Reparto antes de usar las cifras para decidir, y los vehículos ya registrados necesitan que se les cargue el precio de compra y la vida útil para entrar al costo del ciclo de vida.
- Un reporte de un mes completo tarda unos 7.5 s en Render (CPU 0.1); si el sistema pasara a un plan con más CPU bajaría casi todo ese tiempo. Tampoco se midió Lighthouse sobre la pantalla Sostenibilidad ya desplegada en Vercel: la medición de este documento es local, con datos sintéticos.

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: módulo de sostenibilidad, supuestos configurables, pantalla y resultados de pruebas de HU-015 y HU-017 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-23 | Se agregan el reporte PDF y el costo del ciclo de vida de la flota (HU-016), sus pruebas (HT-12), la auditoría y optimización de consultas (HT-11) y se corrige el periodo del sprint | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-23 | Se agrega la medición en Render de los tres endpoints (dashboard, compensación y reporte PDF) y se actualizan las limitaciones | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-30 | Se actualiza el enlace al plan de ejecución a su versión V_1_4_0; el contenido no cambia | Inciso Aguilar Elizabeth Antonela |
