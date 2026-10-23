# 02 Implementación de la sostenibilidad (dashboard y plan de compensación)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (31 oct – 13 nov 2026) |
| **Historias cubiertas** | HU-015 (dashboard de indicadores) y HU-017 (plan de compensación de carbono) |
| **Fecha de corte** | 2026-10-23 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Alcance

Este documento describe lo implementado para las dos primeras historias de la épica EP-07 (Sostenibilidad). El reporte en PDF (HU-016) y la optimización de consultas (HT-11) se documentan cuando se cierren. El estado de cada ítem está en el [`01 Sprint 4 Plan de ejecución y estado`](01%20Sprint%204%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_0_0.md).

## 2. Módulo `sostenibilidad` del backend

Un módulo nuevo, `backend/src/sostenibilidad/`, con la misma organización por características del resto del backend (router → servicio → repositorio). **No importa código de otros módulos de negocio**: consulta las tablas `rutas`, `ruta_pedidos`, `pedidos` y `metricas_sostenibilidad` con su propio SQL parametrizado, igual que `flota` consulta `rutas`. La prueba de arquitectura (`test_arquitectura.py`) lo vigila.

| Endpoint | Rol | Respuesta |
|---|---|---|
| `GET /api/sostenibilidad/dashboard?desde=&hasta=` | ADMINISTRADOR | Totales del periodo (rutas, distancia, CO₂, combustible, combustible ahorrado, ahorro en soles, cumplimiento de ventanas), entregas realizadas, pendientes y fallidas, y serie de emisiones por día |
| `GET /api/sostenibilidad/compensacion?desde=&hasta=` | ADMINISTRADOR | CO₂ del periodo, árboles necesarios, comparación del mes con la meta mensual, acciones de reducción y alianzas de reforestación a explorar |

- **Periodo.** Sin fechas se toma el mes en curso hasta hoy (hora de Perú). No puede ser invertido ni abarcar un año o más: en esos casos responde 422.
- **Qué cuenta.** Las rutas `CONFIRMADA`, `EN_EJECUCION` y `COMPLETADA` cuya fecha de jornada cae en el periodo. Un borrador (`PLANIFICADA`) o una ruta cancelada no es una jornada realizada y no suma. Las entregas excluyen los pedidos cancelados.
- **Cálculos.**
  - Emisiones y distancia: suma de `metricas_sostenibilidad` (la emisión de cada ruta ya es distancia × factor de emisión del vehículo, RN-009).
  - Cumplimiento de ventanas: promedio de las rutas ponderado por su número de paradas.
  - Ahorro económico: combustible ahorrado × precio del litro. Se calcula al consultar y no se guarda, porque el precio es un supuesto ajustable; la columna `ahorro_soles` sigue existiendo en la tabla, pero no se usa.
  - Árboles necesarios (RN-011): emisiones del periodo ÷ kilogramos de CO₂ que absorbe un árbol al año, redondeado hacia arriba.
  - Meta mensual (RN-010): se compara el mes de la fecha final, desde su día 1, con la meta; si la supera, se devuelve la alerta y tres acciones de reducción.
- **Sin datos.** Con el periodo vacío el dashboard devuelve todo en cero y el mensaje «No hay jornadas operativas registradas en el periodo seleccionado.», y el plan pide ejecutar al menos una jornada operativa y no propone alianzas.
- **Permisos.** Solo el administrador (RN-014); el operador y el conductor reciben 403.

## 3. Supuestos configurables

No hay datos reales de la empresa ficticia, así que estos valores son **supuestos declarados** y se ajustan con una variable de entorno en mayúsculas, sin tocar el código (`backend/src/core/config.py`):

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `PRECIO_COMBUSTIBLE_SOLES_L` | 4.50 (soles por litro) | Convierte el combustible ahorrado en soles |
| `META_MENSUAL_CO2_KG` | 800 (kg al mes) | Umbral de la alerta de la RN-010 |
| `KG_CO2_POR_ARBOL_ANIO` | 22 (kg por árbol al año) | Cantidad de árboles de la RN-011; con este valor una tonelada pide unos 46 árboles |

Las **alianzas de reforestación** que muestra el plan son propuestas de tipos de organización a contactar (Gobierno Regional de Junín y SERFOR, comunidades campesinas de la provincia de Huancayo, universidades e institutos). **No hay convenios firmados** con ninguna institución y la pantalla lo dice.

## 4. Pantalla Sostenibilidad del frontend

- Ruta `/app/sostenibilidad`, solo visible para el administrador (el operador no la ve en el menú y, si escribe la dirección, vuelve al mapa).
- Filtro de periodo con atajos «Hoy», «Últimos 7 días» y «Este mes», más fechas «Desde» y «Hasta». Por defecto, el mes en curso.
- Cinco indicadores con una ayuda que explica cómo se calcula cada uno, el resumen de jornadas y entregas, el gráfico de emisiones por día (con el valor en texto) y el plan de compensación con la barra de la meta mensual.
- Cuando el mes supera la meta se muestra una alerta con las acciones sugeridas; cuando no hay datos, un aviso en lugar de cifras inventadas.
- Se adapta al ancho del celular sin desplazamiento horizontal. La pantalla consulta el dashboard y el plan a la vez, con dos peticiones.

## 5. Pruebas y resultados

Mediciones del 23-10-2026, en esta máquina y con la base real:

| Prueba | Resultado |
|---|---|
| Backend (`test_sostenibilidad.py`, contra la base real) | 14 pruebas: periodo por defecto, periodo inválido, borrador que no cuenta, suma de métricas contra la base, relación entre emisiones y factores de emisión, ahorro en soles, entregas y pedidos cancelados, ceros y mensaje, árboles y meta (con un repositorio simulado), permisos por rol |
| Prueba de arquitectura | Pasa con el módulo nuevo |
| Análisis estático (Bandit sobre el módulo) | Sin hallazgos |
| Vitest (`SostenibilidadPage.test.tsx`) | 6 pruebas; el frontend completo suma 95 |
| Playwright de escritorio (`sostenibilidad.spec.ts`) | 4 pruebas: indicadores y plan con alerta, atajo «Hoy», periodo sin datos y el operador sin acceso |
| Playwright en celular | 1 prueba nueva: sin desplazamiento horizontal |
| Lighthouse (Sostenibilidad) | Escritorio 100 en todo; móvil: rendimiento 97, accesibilidad, buenas prácticas y SEO en 100 |
| Validador W3C (Sostenibilidad) | 0 errores y 0 avisos |

## 6. Limitaciones conocidas

- Tras una re-optimización, las métricas de la ruta cubren solo el tramo restante (ver [`02 Implementación de la re-optimización`](../Sprint%203/02%20Implementaci%C3%B3n%20de%20la%20re-optimizaci%C3%B3n%20V_1_3_0.md)); el dashboard puede quedar por debajo de lo recorrido en las rutas re-optimizadas del periodo.
- El combustible ahorrado se mide frente a la solución inicial del optimizador, no frente a una operación real sin optimizar.
- Los tres supuestos de la sección 3 deben validarse con Andina Reparto antes de usar las cifras para decidir.
- Falta medir el tiempo de respuesta de las dos consultas en Render, donde cada petición cuesta unos 2 s (IMP-016).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: módulo de sostenibilidad, supuestos configurables, pantalla y resultados de pruebas de HU-015 y HU-017 | Inciso Aguilar Elizabeth Antonela |
