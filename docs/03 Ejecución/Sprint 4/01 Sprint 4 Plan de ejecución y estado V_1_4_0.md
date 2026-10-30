# 01 Sprint 4 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22 oct – 13 nov 2026) |
| **Fecha de corte** | 2026-10-23 |
| **Inspección** | Por confirmar (no hay fecha; por ahora solo clases) |
| **Versión** | 1.4.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_1_0.md)):

> *Implementar el dashboard de sostenibilidad, reportes PDF y plan de compensación de carbono (EP-07). Ejecutar pruebas de aceptación, completar la documentación técnica y preparar la sustentación final.*

El sprint compromete **5 ítems y 18 Story Points** (3 Historias de Usuario y 2 Historias Técnicas), confirmados contra el tablero de Jira el 23-10-2026 (el sprint se inició en Jira el 22-10-2026 y cierra el 13-11-2026). El trabajo arrancó apenas cerró el Sprint 3 en `main`, para tener margen antes de la actividad de cierre descrita en la sección 5.

## 2. Alcance comprometido y estado al 2026-10-23

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem ya existe y está verificada) y **Pendiente** (sin implementación). El responsable es el que figura en el tablero de Jira.

| ID | Título | Épica | SP | Responsable (Jira) | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|---|
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | EP-07 | 5 | Espinoza Tiza Yago Imanol | Completada | Implementada y probada: módulo `sostenibilidad`, indicadores por periodo, ahorro en soles, ceros con mensaje sin datos y pantalla del administrador; Lighthouse 97 a 100 y W3C sin errores (ver [`02 Implementación de la sostenibilidad`](02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_3_0.md)); medida en Render (ver el documento de implementación): dashboard 2.4 s con 450 rutas | — |
| HU-016 | Descargar reporte de sostenibilidad en PDF | EP-07 | 5 | Espinoza Tiza Yago Imanol | Completada | Implementada y probada: PDF con CO₂ por ruta, costo del ciclo de vida de la flota (precio de compra y vida útil del vehículo), ahorro de combustible y metas; reporte parcial si hay jornadas sin completar; 404 con mensaje sin datos; botón de descarga y registro de auditoría (ver [`02 Implementación de la sostenibilidad`](02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_3_0.md)); medida en Render (ver el documento de implementación): reporte de 30 días en 7.5 s y de 1 día en 3.3 s | Cargar el precio de compra y la vida útil de los vehículos reales (dato de la empresa; sin él, esos vehículos salen como «sin dato») |
| HU-017 | Consultar plan de compensación de carbono | EP-07 | 3 | Espinoza Tiza Yago Imanol | Completada | Implementada y probada: árboles necesarios (RN-011), alerta con acciones si el mes supera la meta (RN-010), alianzas a explorar y mensaje sin datos, en la misma pantalla; medida en Render (ver el documento de implementación): plan de compensación 2.3 s | — |
| HT-11 | Optimizar consultas SQL aplicando Green Software | EP-07 | 3 | Guerra Lozano Keen | Completada | Auditoría de 17 consultas críticas con un volumen de seis meses de operación (`scripts/auditar_consultas.py`): todas en 42 ms o menos en el servidor y ninguna sin índice; índice `idx_pedidos_creado` (listado de pedidos de 7.0 a 0.1 ms) y dashboard y reporte que cuentan solo las paradas del periodo (de 6.6 a 3.1 ms y de 6.9 a 2.5 ms) | — |
| HT-12 | Pruebas de generación de reportes PDF | EP-07 | 2 | Espinoza Tiza Yago Imanol | Completada | 15 pruebas de `test_reporte_pdf.py`: PDF válido leído de vuelta con `pypdf`, sin PDF vacío cuando no hay datos, costo del ciclo de vida, reporte parcial, descarga por la API y permisos; 2 de Flota para los campos nuevos | — |

**Resumen del corte:** 5/5 ítems completados al 2026-10-23 (18 de 18 SP), desplegados y medidos en Render. El criterio 3 del DoD (aprobación de un compañero) se cumplió en el Pull Request #64, aprobado por Espinoza Tiza Yago Imanol y Guerra Lozano Keen antes del merge. El sprint lleva 2 de 23 días.

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
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov sobre el código nuevo; Vitest para el frontend nuevo | **Cumplido:** el módulo `sostenibilidad` tiene 100 % (total del backend 98 %, 359 pruebas); Vitest suma 99 |
| 2 | Análisis estático | 0 vulnerabilidades críticas (Bandit, pip-audit, npm audit) en el workflow de GitHub Actions | **Cumplido:** el workflow quedó en verde en los PR #62 y #63; Bandit, pip-audit y npm audit sin hallazgos |
| 3 | Revisión de código | Pull Request aprobado por un compañero en GitHub antes del merge a `main` (en el Sprint 3 solo el #60 lo cumplió; aquí se pide en todos) | **Cumplido en el #64:** el Pull Request de documentación fue aprobado en GitHub el 23-10-2026 por YagoEspinoza (19:25 UTC) y KeenGuerra (19:27 UTC), ambos colaboradores del repositorio, antes del merge (19:28 UTC). El #62 y el #63 se habían fusionado antes, sin aprobación registrada en GitHub |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | **Cumplido:** Render sirve los tres endpoints nuevos y Vercel la pantalla con el botón del reporte |
| 5 | Documentación de API | Endpoints nuevos documentados en Swagger/OpenAPI | **Cumplido:** `/api/sostenibilidad/dashboard`, `/compensacion` y `/reporte` aparecen en `/docs` |
| 6 | Criterios de aceptación verificados | Escenarios de HU-015, HU-016, HU-017, HT-11 y HT-12 ejecutados y aprobados | **Cumplido:** los dos escenarios de cada ítem tienen pruebas de integración y de extremo a extremo |
| 7 | Cumplimiento de estándares | Lighthouse ≥ 90 y W3C sin errores en cada pantalla nueva, medidos al terminarla | **Cumplido:** Sostenibilidad con Lighthouse 95 a 99 en rendimiento y 100 en el resto, y W3C sin errores |
| 8 | Commit en rama e integración por Pull Request | Rama `sprint4` integrada a `main` por bloque terminado | **Cumplido:** PR #62 y #63 |

## 5. Actividad de cierre del proyecto (después del Sprint 4)

El docente entregó el material «Revisión de código, OWASP, WCAG y usabilidad». No es solo SonarQube: pide analizar OWASP Top 10 2025, evaluar WCAG 2.2, aplicar la escala SUS en positivo y las heurísticas de Nielsen, y ejecutar SonarQube sobre la aplicación, corrigiendo lo verificable. Se acordó con el docente usar SonarQube Cloud **al terminar todos los sprints**. **Estado al 30-10-2026:** SonarQube Cloud, OWASP Top 10 2025 y WCAG 2.2 están **hechos y documentados el 30-10-2026** en `docs/03 Ejecución/Sprint 3/Implementación/` (documentos 05, 06 y 07), con el Quality Gate de SonarQube aprobado; la escala SUS y las heurísticas de Nielsen siguen pendientes (semana 14 del cronograma del curso).

| Actividad | Cobertura actual | Falta o resultado |
|---|---|---|
| SonarQube Cloud sobre backend y frontend | Bandit, pip-audit, npm audit y oxlint en CI | **Hecho el 30-10-2026:** Quality Gate aprobado, 0 vulnerabilidades y 18 incidencias de mantenibilidad justificadas (`05 Calidad de código`) |
| OWASP Top 10 2025 | Autenticación con MFA, RLS, control por rol, auditoría y análisis estático | **Hecho:** matriz de las 10 categorías de 2025 y plan de brechas (`06 Evaluación de seguridad OWASP`) |
| WCAG 2.2 | Lighthouse de accesibilidad en 100 y W3C sin errores (criterios de WCAG 2.1 AA) | **Hecho:** evaluación de los cuatro principios y de los criterios nuevos de la 2.2 (`07 Evaluación de accesibilidad WCAG`) |
| Usabilidad: SUS en positivo y heurísticas de Nielsen | — | Aplicar el cuestionario al equipo y a usuarios de prueba, y evaluar las heurísticas |

## 6. Plan de trabajo (23-10 → 13-11)

Propuesta **sujeta a validación del equipo**. La fecha de inspección no está confirmada; el plan asume el cierre del 13-11.

| Fecha | Foco | Resultado verificable |
|---|---|---|
| 23-10 a 25-10 | HU-015: backend de métricas y pantalla del dashboard | Escenarios 1 y 2 en la API y en pantalla |
| 26-10 a 30-10 | HU-017 y HU-016: plan de compensación y reporte PDF | Escenarios de ambas historias; ciclo de vida de la flota |
| 31-10 a 03-11 | HT-11 y HT-12: consultas SQL, índices y pruebas de reportes | Consultas críticas ≤ 500 ms; pruebas del PDF |
| 04-11 a 08-11 | Calidad de las pantallas nuevas: Lighthouse, W3C y pruebas de extremo a extremo | Evidencias de calidad |
| 09-11 a 13-11 | Cierre: documentos, revisión y retrospectiva del sprint | DoD |
| Después (30-10) | Actividad de cierre de la sección 5 | SonarQube, OWASP y WCAG 2.2 hechos; SUS y heurísticas de Nielsen pendientes |

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
- Implementación de HU-015 y HU-017: [`02 Implementación de la sostenibilidad`](02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_3_0.md).
- Estado del sprint anterior: [`01 Sprint 3 Plan de ejecución y estado V_1_7_0`](../Sprint%203/01%20Sprint%203%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_7_0.md).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: alcance del Sprint 4 (18 SP), decisiones de alcance, actividad de cierre y plan de trabajo | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-23 | Se corrige el periodo del sprint según Jira (22-10 a 13-11, ya iniciado), se agrega el responsable por ítem y el avance de los cinco ítems: HT-11 y HT-12 completadas, HU-015, HU-016 y HU-017 parciales | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-23 | HU-015, HU-016 y HU-017 pasan a Completadas (18 de 18 SP) tras desplegar y medir en Render; se actualiza el Definition of Done; se registra la aprobación de dos compañeros en el Pull Request #64 (criterio 3) | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-23 | Se registra la aprobación del Pull Request #64 por dos compañeros (criterio 3 del Definition of Done); el #62 y el #63 se fusionaron antes sin aprobación registrada | Inciso Aguilar Elizabeth Antonela |
| V_1_4_0 | 2026-10-30 | Se actualiza la actividad de cierre: SonarQube Cloud (Quality Gate aprobado), OWASP Top 10 2025 y WCAG 2.2 quedan hechos y documentados en el Sprint 3; la escala SUS y las heurísticas de Nielsen siguen pendientes | Inciso Aguilar Elizabeth Antonela |
