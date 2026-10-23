# 03 Revisión del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026) |
| **Fecha de la revisión** | Por confirmar (contenido al 23-10-2026) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Documento preparado el 23-10-2026**, con el alcance comprometido ya completo y antes de la inspección, cuya fecha aún no está confirmada. Se actualiza si algo cambia hasta entonces.

## Historias de Usuario completadas en este Sprint

Compromiso del sprint: 5 ítems y 18 Story Points. Detalle y evidencias en [`01 Sprint 4 Plan de ejecución y estado`](../01%20Sprint%204%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_3_0.md) y en [`02 Implementación de la sostenibilidad`](../02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_2_0.md).

| ID | Historia | Épica | SP | Estado |
|---|---|---|---|---|
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | EP-07 Sostenibilidad | 5 | Completada |
| HU-016 | Descargar reporte de sostenibilidad en PDF | EP-07 Sostenibilidad | 5 | Completada |
| HU-017 | Consultar plan de compensación de carbono | EP-07 Sostenibilidad | 3 | Completada |
| HT-11 | Optimizar consultas SQL aplicando principios Green Software | EP-07 Sostenibilidad | 3 | Completada |
| HT-12 | Pruebas de generación de reportes PDF | EP-07 Sostenibilidad | 2 | Completada |

**Resultado: 18 de 18 Story Points (100 %).**

## Demostración del trabajo completado

Orden previsto para la demostración (máximo 10 minutos):

1. **Pantalla Sostenibilidad** (HU-015): elegir «Este mes» y mostrar los cinco indicadores (distancia, CO₂, combustible ahorrado, cumplimiento de ventanas y ahorro en soles) con su ayuda, el resumen de entregas y el gráfico de emisiones por día. Cambiar a un periodo sin jornadas para mostrar los ceros y el aviso.
2. **Plan de compensación** (HU-017): árboles necesarios para compensar el CO₂ del periodo, la barra de la meta mensual y, si el mes la supera, la alerta con las acciones sugeridas y las alianzas de reforestación a explorar.
3. **Reporte PDF** (HU-016): «Descargar reporte PDF» y abrir el archivo: resumen, CO₂ por ruta, costo del ciclo de vida de la flota, metas y supuestos. Descargar uno de un periodo sin datos para mostrar el aviso en lugar de un PDF vacío.
4. **Ciclo de vida del vehículo**: en Flota, registrar el precio de compra y la vida útil de un vehículo y repetir el reporte para ver cómo cambia su costo.
5. **Consultas de la base** (HT-11): ejecutar `python scripts/auditar_consultas.py`, que carga seis meses de datos en una transacción que se deshace y muestra los 17 tiempos y los índices usados.
6. **Evidencias de calidad**: integración continua en verde, 359 pruebas del backend con 98 % de cobertura, Playwright, Lighthouse y W3C de la pantalla.

Preparación: calentar Render unos minutos antes (el servicio gratuito tarda entre 30 y 45 s en despertar), generar y confirmar las rutas de la jornada para que haya métricas en el periodo, y cargar el precio de compra y la vida útil de al menos un par de vehículos. El reporte de un mes tarda cerca de 8 s en Render: conviene explicarlo mientras se genera.

### Resultados medidos

| Criterio | Meta | Resultado |
|---|---|---|
| Dashboard en Render (30 días, 450 rutas) | — | **2.4 s** (2.3 s con 15 rutas): el tiempo es de red hacia la base |
| Plan de compensación en Render (30 días) | — | **2.3 s** |
| Reporte PDF en Render | — | **7.5 s** el de 30 días (300 rutas listadas) y **3.3 s** el de un día |
| Consultas críticas de la base (RNF-011, HT-11) | ≤ 500 ms | **17 de 17 en 42 ms o menos** en el servidor, con un volumen de seis meses (2 700 rutas y 16 200 pedidos) |
| Listado de pedidos sin filtro | — | De 7.0 ms a **0.1 ms** con el índice `idx_pedidos_creado` |
| Dashboard y reporte del periodo | — | De 6.6 a 3.1 ms y de 6.9 a 2.5 ms al contar solo las paradas del periodo |
| Cobertura de pruebas del backend | ≥ 80 % | **98 %** (359 pruebas); el módulo `sostenibilidad`, **100 %** |
| Pruebas del frontend | — | 99 de Vitest y 26 de Playwright (escritorio y móvil) |
| Integración continua (GitHub Actions) | en verde | En los Pull Request #62 a #65 y en las integraciones a `main` |
| Seguridad | 0 críticas | Bandit sin hallazgos, `pip-audit` y `npm audit` sin vulnerabilidades |
| Lighthouse de Sostenibilidad (local, datos sintéticos) | ≥ 90 | Accesibilidad, buenas prácticas y SEO en **100**; rendimiento **99** en escritorio y **95** en móvil |
| Validación W3C de Sostenibilidad (DOM renderizado) | sin errores | 0 errores y 0 avisos |

**Salvedades:**

- El precio del combustible (S/ 4.50 por litro), la meta mensual de CO₂ (800 kg) y el CO₂ que absorbe un árbol (22 kg al año) son **supuestos sin datos reales de la empresa**; se ajustan por variable de entorno y las alianzas de reforestación son propuestas, sin convenios firmados.
- El costo del ciclo de vida solo incluye los vehículos con precio de compra y vida útil registrados; los demás salen como «sin dato» y no suman.
- Tras una re-optimización, las métricas de una ruta cubren solo el tramo restante, así que el dashboard y el reporte pueden quedar por debajo de lo recorrido en esas rutas.
- El combustible ahorrado se mide frente a la solución inicial del optimizador, no frente a una operación real sin optimizar.
- El Lighthouse de esta pantalla es local con datos sintéticos; falta medirlo sobre la versión desplegada en Vercel.

### Trabajo adicional al compromiso

Entre otros: el script repetible de auditoría de consultas (`scripts/auditar_consultas.py`), los campos de precio de compra y vida útil en el formulario y el detalle de Flota, el registro de cada descarga del reporte en la auditoría, el cliente de la API con descarga de archivos y renovación de sesión, el script de medición de sostenibilidad en Render, y la inclusión del módulo nuevo en la medición de cobertura.

## Pendientes

- **Actividad de cierre del proyecto** (material del docente «Revisión de código, OWASP, WCAG y usabilidad»), al terminar todos los sprints: SonarQube Cloud sobre backend y frontend, mapeo a OWASP Top 10 2025, revisión de WCAG 2.2 y evaluación de usabilidad con la escala SUS en positivo y las heurísticas de Nielsen.
- **Datos de la flota real**: cargar el precio de compra y la vida útil de los vehículos y validar los tres supuestos con la empresa.
- **Lighthouse en producción** de la pantalla Sostenibilidad.
- **Pruebas de aceptación, documentación técnica y sustentación final**, parte de la meta del sprint en Jira.
- **Rendimiento en Render**: reutilizar las matrices entre peticiones y reducir los viajes a la base (IMP-016, IMP-019).
- **Integración continua, fase 2**: las pruebas de pytest contra Supabase se reevalúan al cerrar todos los sprints.
- **Heredados**: foto del conductor con Cloudinary, calibración de los factores de hora punta, checklist formal de políticas RLS y versión de Python fijada en Render.
- **Aprobación de los Pull Request por un compañero** (criterio 3 del Definition of Done): el Pull Request #64 fue aprobado en GitHub por Yago Espinoza y Keen Guerra el 23-10-2026, antes del merge; el #62 y el #63 se fusionaron antes, sin aprobación registrada.

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 4) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | Sin ítems propios en el tablero; trabajó junto con Yago en HU-015, HU-016, HU-017 y HT-12 | Construcción de HU-015, HU-016, HU-017, HT-11 y HT-12: el módulo de sostenibilidad, el reporte PDF, el costo del ciclo de vida de la flota, la auditoría y optimización de consultas, las pruebas y las migraciones; mediciones en Render; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-015, HU-016, HU-017, HT-12 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |
| Uscuvilca Ramos Abraham Luis | Sin ítems propios en el tablero; trabajó junto con Keen en HT-11 | Pruebas del sistema como tester |
| Guerra Lozano Keen | HT-11 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |

**Nota de proceso:** los commits y push del repositorio se hacen desde una sola cuenta de GitHub, la de la líder del proyecto, para agilizar la integración. Por eso el historial de Git no refleja por sí solo la autoría de cada integrante y este cuadro es la referencia de quién aportó en qué. Las revisiones se hacen en persona, desde la computadora de la líder, cuando el equipo trabaja junto en clase.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: resultado (18 de 18 SP), demostración de 10 minutos, resultados medidos, trabajo adicional y pendientes; el aporte por integrante con lo declarado por la líder | Inciso Aguilar Elizabeth Antonela |
