# 01 Sprint 4 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (31 oct – 13 nov 2026) |
| **Fecha de corte** | 2026-10-23 |
| **Inspección** | Por confirmar (no hay fecha; por ahora solo clases) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_1_0.md)):

> *Implementar el dashboard de sostenibilidad, reportes PDF y plan de compensación de carbono (EP-07). Ejecutar pruebas de aceptación, completar la documentación técnica y preparar la sustentación final.*

El sprint compromete **5 ítems y 18 Story Points** (3 Historias de Usuario y 2 Historias Técnicas), confirmados contra el tablero de Jira el 23-10-2026 (el sprint todavía no se ha iniciado en Jira). El trabajo empieza antes del 31-10, apenas cerró el Sprint 3 en `main`, para tener margen antes de la actividad de cierre descrita en la sección 5.

## 2. Alcance comprometido y estado al 2026-10-23

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem ya existe y está verificada) y **Pendiente** (sin implementación). El responsable es el que figura en el tablero de Jira.

| ID | Título | Épica | SP | Responsable (Jira) | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|---|
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | EP-07 | 5 | Espinoza Tiza Yago Imanol | Parcial | Implementada y probada: módulo `sostenibilidad`, indicadores por periodo, ahorro en soles, ceros con mensaje sin datos y pantalla del administrador; Lighthouse 97 a 100 y W3C sin errores (ver [`02 Implementación de la sostenibilidad`](02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_0_0.md)) | Medir en Render, la revisión de un compañero y el resumen del día para el conductor (recortable) |
| HU-016 | Descargar reporte de sostenibilidad en PDF | EP-07 | 5 | Espinoza Tiza Yago Imanol | Pendiente | — | Generación del PDF (CO₂ por ruta, costo del ciclo de vida de la flota, ahorro de combustible, metas), reporte parcial si la jornada sigue en curso, mensaje si no hay datos |
| HU-017 | Consultar plan de compensación de carbono | EP-07 | 3 | Espinoza Tiza Yago Imanol | Parcial | Implementada y probada: árboles necesarios (RN-011), alerta con acciones si el mes supera la meta (RN-010), alianzas a explorar y mensaje sin datos, en la misma pantalla | Medir en Render y la revisión de un compañero |
| HT-11 | Optimizar consultas SQL aplicando Green Software | EP-07 | 3 | Guerra Lozano Keen | Pendiente | Índices del listado de pedidos (HT-08) | Medir las consultas críticas con 150 pedidos (≤ 500 ms), revisar planes de ejecución y agregar los índices que falten |
| HT-12 | Pruebas de generación de reportes PDF | EP-07 | 2 | Espinoza Tiza Yago Imanol | Pendiente | — | Pruebas del módulo de reportes (PDF válido con datos y error esperado sin datos) |

**Resumen del corte:** 0/5 ítems completados al 2026-10-23 (0 de 18 SP). HU-015 (5 SP) y HU-017 (3 SP) están implementadas y probadas, a falta de la medición en Render y de la revisión de un compañero. El sprint formal empieza el 31-10.

## 3. Decisiones de alcance

| Tema | Decisión | Motivo |
|---|---|---|
| Costo del ciclo de vida de la flota (HU-016) | Se agregan al vehículo el **precio de compra** y la **vida útil en años**; el costo del periodo es compra ÷ vida útil (prorrateada por días) más el combustible gastado | Decidido con la líder del proyecto; el dato lo aporta Andina Reparto al registrar el vehículo y el reporte no depende de números inventados por tipo de vehículo |
| Datos que cuentan | Rutas confirmadas, en ejecución o completadas; los borradores no se incluyen | Un borrador no es una operación realizada |
| Supuestos configurables | Precio del litro de combustible, meta mensual de CO₂ y árboles por tonelada de CO₂ son **supuestos** declarados en el documento de implementación y ajustables por configuración | No hay datos reales de la empresa ficticia; la misma política que las franjas de hora punta del Sprint 3 |

## 4. Definition of Done — metas del sprint

Criterios del DoD global ([`01 Transformando a ágil`](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_1_0.md), sección 5), aplicados a lo que entregue este sprint:

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov sobre el código nuevo; Vitest para el frontend nuevo | Pendiente |
| 2 | Análisis estático | 0 vulnerabilidades críticas (Bandit, pip-audit, npm audit) en el workflow de GitHub Actions | Pendiente |
| 3 | Revisión de código | Pull Request aprobado por un compañero en GitHub antes del merge a `main` (en el Sprint 3 solo el #60 lo cumplió; aquí se pide en todos) | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints nuevos documentados en Swagger/OpenAPI | Pendiente |
| 6 | Criterios de aceptación verificados | Escenarios de HU-015, HU-016, HU-017, HT-11 y HT-12 ejecutados y aprobados | Pendiente |
| 7 | Cumplimiento de estándares | Lighthouse ≥ 90 y W3C sin errores en cada pantalla nueva, medidos al terminarla | Pendiente |
| 8 | Commit en rama e integración por Pull Request | Rama `sprint4` integrada a `main` por bloque terminado | Pendiente |

## 5. Actividad de cierre del proyecto (después del Sprint 4)

El docente entregó el material «Revisión de código, OWASP, WCAG y usabilidad». No es solo SonarQube: pide analizar OWASP Top 10 2025, evaluar WCAG 2.2, aplicar la escala SUS en positivo y las heurísticas de Nielsen, y ejecutar SonarQube sobre la aplicación, corrigiendo lo verificable. Se acordó con el docente usar SonarQube Cloud **al terminar todos los sprints**.

| Actividad | Cobertura actual | Falta |
|---|---|---|
| SonarQube Cloud sobre backend y frontend | Bandit, pip-audit, npm audit y oxlint en CI | Ejecutar SonarQube Cloud, corregir los hallazgos verificables y documentarlos |
| OWASP Top 10 2025 | Autenticación con MFA, RLS, control por rol, auditoría y análisis estático | Mapear cada categoría a lo implementado y registrar las brechas |
| WCAG 2.2 | Lighthouse de accesibilidad en 100 y W3C sin errores (criterios de WCAG 2.1 AA) | Revisar los criterios nuevos de la 2.2 |
| Usabilidad: SUS en positivo y heurísticas de Nielsen | — | Aplicar el cuestionario al equipo y a usuarios de prueba, y evaluar las heurísticas |

## 6. Plan de trabajo (23-10 → 13-11)

Propuesta **sujeta a validación del equipo**. La fecha de inspección no está confirmada; el plan asume el cierre del 13-11.

| Fecha | Foco | Resultado verificable |
|---|---|---|
| 23-10 a 25-10 | HU-015: backend de métricas y pantalla del dashboard | Escenarios 1 y 2 en la API y en pantalla |
| 26-10 a 30-10 | HU-017 y HU-016: plan de compensación y reporte PDF | Escenarios de ambas historias; ciclo de vida de la flota |
| 31-10 a 03-11 | HT-11 y HT-12: consultas SQL, índices y pruebas de reportes | Consultas críticas ≤ 500 ms; pruebas del PDF |
| 04-11 a 08-11 | HT-09 y HT-10 del cierre: Lighthouse, W3C y pruebas de extremo a extremo de las pantallas nuevas | Evidencias de calidad |
| 09-11 a 13-11 | Cierre: documentos, revisión y retrospectiva del sprint | DoD |
| Después | Actividad de cierre de la sección 5 | SonarQube, OWASP, WCAG 2.2 y SUS |

**Orden de recorte si el tiempo no alcanza:** (1) resumen del día en la vista del conductor; (2) alianzas de reforestación con más de un proyecto; (3) reporte parcial por jornada en curso, manteniendo el reporte de periodos cerrados. HU-015, el PDF básico y el plan de compensación se mantienen como núcleo.

## 7. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Latencia de la base en Render gratuito (IMP-016): cada consulta cuesta unos 2 s | Dashboard lento y Lighthouse bajo 90 | Una sola consulta agregada por pantalla y medir en Render desde el primer día |
| Generar el PDF en un servicio con 0.1 CPU | Tiempo de respuesta alto o agotado | Biblioteca ligera de PDF, un solo documento de pocas páginas y medición en Render |
| Los factores de combustible, la meta de CO₂ y los árboles por tonelada son supuestos | Cifras que no reflejan la operación real | Declararlos como supuestos y dejarlos configurables |
| La revisión de cada Pull Request por un compañero no se hizo en todos los del Sprint 3 | Criterio 3 del DoD incumplido | Pedir la aprobación en GitHub antes de cada merge |

## 8. Evidencias

- Código del backend: [`backend/`](../../../backend/) y del frontend: [`frontend/`](../../../frontend/).
- Implementación de HU-015 y HU-017: [`02 Implementación de la sostenibilidad`](02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_0_0.md).
- Estado del sprint anterior: [`01 Sprint 3 Plan de ejecución y estado V_1_7_0`](../Sprint%203/01%20Sprint%203%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_7_0.md).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: alcance del Sprint 4 (18 SP), decisiones de alcance, actividad de cierre y plan de trabajo | Inciso Aguilar Elizabeth Antonela |
