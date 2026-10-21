# 01 Sprint 3 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Fecha de corte** | 2026-10-20 |
| **Inspección** | Por confirmar (Jira cierra el sprint el 30-10-2026) |
| **Versión** | 1.3.0 |

[← Volver al README Principal](../../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_1_0.md)):

> *Completar el motor de optimización ACO con re-optimización dinámica (EP-05) e implementar la visualización de rutas en mapa interactivo con Leaflet + OpenStreetMap (EP-06).*

El sprint compromete **5 ítems y 26 Story Points** (3 Historias de Usuario y 2 Historias Técnicas), confirmados contra el tablero de Jira el 20-10-2026. Cierra además HT-07, que quedó parcial en el Sprint 2 por depender de HU-012.

## 2. Alcance comprometido y estado al 20-10-2026

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem ya existe y está verificada) y **Pendiente** (sin implementación).

| ID | Título | Épica | SP (Jira) | Responsable (Jira) | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|---|
| HU-012 | Re-optimizar rutas ante evento de cambio operativo | EP-05 | 8 | Inciso Aguilar Elizabeth Antonela | Completada | Re-optimización ante pedido urgente, cancelación o incidente de tráfico sin alterar lo ya entregado, caso «sin rutas activas», registro de entregas, incidentes y pantalla; 288 pruebas del backend (98 %) y 60 del frontend; **en Render, 27.1 a 27.2 s en el servidor y 29.0 s desde fuera con 150 pedidos y 15 vehículos; tras ampliar el margen (presupuesto de 25 s) y con las horas punta, 22.2 s y 24.0 s** (ver [`02 Implementación de la re-optimización`](../02%20Implementaci%C3%B3n%20de%20la%20re-optimizaci%C3%B3n%20V_1_3_0.md)) | Revisión del Pull Request por un compañero |
| HU-013 | Visualizar rutas optimizadas en mapa interactivo | EP-06 | 5 | Espinoza Tiza Yago Imanol | Completada | Mapa con el recorrido por calles de cada ruta, paradas con su estado, tiempo y distancia por tramo, vías en verde, amarillo o rojo según la hora (horas punta de RF-003 e incidentes), refresco cada 30 s y mensaje sin rutas; 313 pruebas del backend (98 %) y 73 del frontend; revisada en local y medida en Render (mapa: 9.3 s la primera carga y 2.6 s desde la caché; ver [`04 Implementación del mapa de rutas`](../04%20Implementaci%C3%B3n%20del%20mapa%20de%20rutas%20V_1_1_0.md)) | Lighthouse y W3C de la pantalla (HT-09); revisión del Pull Request |
| HU-014 | Visualizar ruta asignada en modo conductor | EP-06 | 3 | Espinoza Tiza Yago Imanol | Pendiente | Vista mobile del conductor (Sprint 1) | Ruta propia, entregas pendientes y alertas de tráfico en formato simplificado; mensaje si no tiene ruta asignada |
| HT-09 | Implementar diseño responsive y cumplimiento WCAG 2.1 AA | EP-06 | 5 | Uscuvilca Ramos Abraham Luis | Pendiente | Lighthouse con accesibilidad y SEO en 100 y W3C sin errores en las 8 pantallas actuales (Sprint 2) | Repetir la medición en cada pantalla nueva del sprint, al terminarla; revisión en ancho móvil |
| HT-10 | Pruebas de integración del mapa interactivo | EP-06 | 5 | Uscuvilca Ramos Abraham Luis | Pendiente | Pruebas con Vitest y Testing Library para Mapa y Rutas | Pruebas de extremo a extremo con Playwright; GitHub Actions; estrategia en [`03 Estrategia y resultados de pruebas`](03%20Estrategia%20y%20resultados%20de%20pruebas%20V_1_3_0.md) |
| HT-07 | *(Arrastrado del Sprint 2, sin SP nuevos)* Motor ACO | EP-05 | — | Espinoza Tiza Yago Imanol | Completada | Escenario 1 verificado: 29.1 s con 150 pedidos y 15 vehículos. Escenario 2 verificado en Render con HU-012: re-optimización en 27.1 a 27.2 s | — |

**Resumen del corte:** 2/5 ítems completados al 20-10-2026 (**13 de 26 SP**: HU-012 y HU-013). HT-07, parcial en el Sprint 2, queda cerrada con HU-012. Faltan HU-014 (3 SP), HT-09 y HT-10 (5 SP cada uno). El sprint lleva 4 de 14 días.

## 3. Trabajo heredado del Sprint 2

Deuda técnica y acciones de la retrospectiva del Sprint 2 que se atienden en este sprint:

| Ítem | Responsable propuesto | Estado |
|---|---|---|
| GitHub Actions: pruebas y análisis estático en cada Pull Request | Guerra Lozano Keen | Pendiente; la fase 1 (sin credenciales) se hace dentro de HT-10; los pytest del backend en CI se reevalúan al terminar todos los sprints (ver estrategia de pruebas) |
| Fijar la versión de Python en Render y poner topes en `requirements.txt` | Inciso Aguilar Elizabeth Antonela | Pendiente |
| Reducir los viajes a la base por petición (IMP-016) | Inciso Aguilar Elizabeth Antonela | Pendiente |
| Checklist formal de políticas RLS para toda tabla nueva | Guerra Lozano Keen | Pendiente |
| Foto del conductor con Cloudinary (adicional, fuera del compromiso) | Por definir | Pendiente; primero en recortarse |

## 4. Definition of Done — metas del sprint

Criterios del DoD global ([`01 Transformando a ágil`](../../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_1_0.md), sección 5), aplicados a lo que entregue este sprint:

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov sobre el código nuevo de `rutas/` y `algoritmo/`; Vitest para el frontend nuevo | Pendiente |
| 2 | Análisis estático | 0 vulnerabilidades críticas (Bandit, pip-audit, npm audit), Bandit, pip-audit y npm audit automatizados en GitHub Actions (fase 1) | Pendiente |
| 3 | Revisión de código | Pull Request aprobado por un compañero en GitHub antes del merge a `main` | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints nuevos documentados en Swagger/OpenAPI | Pendiente |
| 6 | Criterios de aceptación verificados | Escenarios de HU-012, HU-013 y HU-014 ejecutados y aprobados | Pendiente |
| 7 | Cumplimiento de estándares | Lighthouse ≥ 90 y W3C sin errores en cada pantalla nueva, medidos al terminarla | Pendiente |
| 8 | Commit en rama e integración por Pull Request | Rama `sprint3` integrada a `main` por bloque terminado | Pendiente |

## 5. Plan de trabajo (20-10 → 30-10)

Propuesta **sujeta a validación del equipo**. La fecha de inspección no está confirmada; el plan asume el cierre del 30-10.

| Fecha | Foco | Resultado verificable |
|---|---|---|
| 20-10 | Documentación de arranque y decisiones de pruebas | Carpeta del Sprint 3 y estrategia de pruebas |
| 21-10 a 23-10 | HU-012: re-optimización en el backend (pedido urgente, cancelación, incidente) y medición de tiempo | Escenarios 1 y 2 en la API; HT-07 cerrado. Completado el 20-10: backend, pantalla y medición en Render (27.1 a 27.2 s) |
| 24-10 a 26-10 | HU-014: vista del conductor con su ruta, sus entregas y las alertas de tráfico (HU-013, con el mapa, el trazado y la congestión por horas punta, quedó completada el 20-10) | HU-014 en pantalla |
| 27-10 | GitHub Actions y pruebas de extremo a extremo con Playwright (HT-10) | Flujos del mapa y del conductor en CI |
| 28-10 | HT-09: Lighthouse y W3C en las pantallas nuevas, revisión en ancho móvil | Evidencias de calidad |
| 29-10 | Cierre: cobertura, análisis estático, Pull Request, documentos | DoD |
| 30-10 | Cierre del sprint en Jira | Revisión y retrospectiva |

**Orden de recorte si el tiempo no alcanza** (de lo primero que se sacrificaría a lo último): (1) foto del conductor con Cloudinary; (2) reducción de viajes a la base (IMP-016); (3) pruebas con varios navegadores en Playwright, manteniendo Chromium; (4) alertas de tráfico de la vista del conductor, manteniendo su ruta y sus entregas. HU-012, el mapa con rutas y la vista del conductor básica se mantienen como núcleo.

## 6. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Re-optimización ≤ 30 s con la CPU limitada de Render gratuito (IMP-013): la generación completa tomó 29.1 s | Incumplir el escenario 1 de HU-012 | Re-optimizar solo las rutas afectadas y partir de la solución vigente, no desde cero; medir en Render desde el primer día |
| La mayor parte del sprint se concentra en pocas personas (IMP-005) | Atrasos en HU-013 y HT-10 | Responsable por ítem según Jira y checkpoint de medio sprint |
| Pruebas de extremo a extremo frágiles o lentas | CI poco confiable | Pocos flujos, API simulada en el navegador y datos controlados; ver estrategia de pruebas |
| Pruebas del backend contra la base real (~7 min) no ejecutables en CI sin credenciales | CI sin pytest | Solo la fase 1 de CI en este sprint; pytest se sigue corriendo localmente antes de cada Pull Request y su paso a CI se reevalúa al cierre del proyecto |
| Rendimiento de Lighthouse en Mapa por la latencia de la API (IMP-016) | Rendimiento bajo 90 | Reducir viajes a la base y diferir la carga de datos del mapa |

## 7. Evidencias

- Código del backend: [`backend/`](../../../../backend/) y del frontend: [`frontend/`](../../../../frontend/).
- Estado del sprint anterior: [`01 Sprint 2 Plan de ejecución y estado V_1_8_0`](../../Sprint%202/01%20Sprint%202%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_8_0.md).
- Entregables de seguimiento: carpeta [`Implementación/`](../Implementaci%C3%B3n/).

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: alcance del Sprint 3 confirmado contra Jira, trabajo heredado del Sprint 2 y plan de trabajo | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-20 | HU-012 y HT-07 pasan a Completadas con la medición en Render (27.1 a 27.2 s en el servidor); resumen y plan de trabajo actualizados | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-20 | HU-013 pasa a Parcial: mapa por calles y congestión por horas punta implementados y probados; falta Lighthouse, W3C y la medición en Render | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-20 | HU-013 pasa a Completada tras medirla en Render; el presupuesto de 25 s deja 24.0 s desde fuera en la re-optimización (13 de 26 SP) | Inciso Aguilar Elizabeth Antonela |
