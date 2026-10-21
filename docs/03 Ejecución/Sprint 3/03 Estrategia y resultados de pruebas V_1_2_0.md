# 03 Estrategia y Resultados de Pruebas

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Fecha** | 2026-10-20 |
| **Versión** | 1.2.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Propósito

Define cómo se organizan las pruebas del proyecto y qué se agrega en el Sprint 3 (HT-10). Toma como referencia el material del docente *El ecosistema de testing en JavaScript (2026)*, que propone una pirámide de pruebas: unitarias, integración y componentes, y extremo a extremo. Los resultados medidos se registran en la sección 5 conforme se obtengan.

## 2. Pirámide de pruebas de RouteZero

| Capa | Herramienta propuesta por el material | Estado en RouteZero | Decisión para el Sprint 3 |
|---|---|---|---|
| Unitarias | Vitest | Vitest en el frontend y pytest en el backend (cobertura total de 96 % al cierre del Sprint 2) | Se mantiene; el código nuevo se prueba en el mismo Pull Request |
| Integración y componentes | Testing Library + MSW | Testing Library con `user-event` y `jest-dom`; sin MSW | Se mantiene Testing Library; **MSW no se instala** (sección 3) |
| Integración de la API | Supertest + base efímera | pytest contra la base real de Supabase, equivalente en función | Se mantiene |
| Extremo a extremo | Playwright | No existía | **Se agrega Playwright** (HT-10) |
| CI/CD | GitHub Actions | No existía | **Se agrega la fase 1**; la fase 2 (pytest) se pospone (sección 4) |

El material del docente establece como regla probar el comportamiento que ve el usuario, no los detalles internos, y preferir roles de accesibilidad y `aria-label` a selectores CSS. Las pruebas nuevas siguen esa regla.

## 3. Decisión sobre MSW

**No se instala MSW en este sprint.** Motivos:

- Las pruebas de componentes del frontend ya sustituyen el cliente de la API con Vitest, y funcionan.
- La simulación de la API que MSW aportaría se cubre en la capa de extremo a extremo con `page.route` de Playwright, que intercepta las peticiones del navegador sin otra dependencia.
- Con el sprint corto, instalar y migrar las pruebas existentes a MSW tendría un costo sin entregar valor a HU-012, HU-013 ni HU-014.

Se reevaluará en el Sprint 4 si las pruebas de componentes se vuelven frágiles ante cambios del contrato de la API (como ocurrió con IMP-017).

## 4. Pruebas de extremo a extremo (Playwright) y CI

**Playwright** (Chromium primero; Firefox y WebKit si el tiempo lo permite; emulación de móvil para la vista del conductor). Flujos previstos para HT-10:

| # | Flujo | Criterio de aceptación relacionado |
|---|---|---|
| 1 | Inicio de sesión y acceso al panel | Autenticación con MFA (Sprint 1) |
| 2 | Mapa con rutas generadas: trazado, puntos de entrega y congestión | HU-013, escenario 1 |
| 3 | Mapa sin rutas: mapa base y mensaje | HU-013, escenario 2 |
| 4 | Vista del conductor con su ruta, en ancho móvil | HU-014, escenario 1 |
| 5 | Conductor sin ruta asignada | HU-014, escenario 2 |
| 6 | Re-optimización y mensaje de "sin rutas activas" | HU-012, escenarios 1 y 2 |

La API se simula en el navegador con `page.route` y datos fijos, de modo que las pruebas no dependen de Render, de Supabase ni de una cuenta real con MFA.

**GitHub Actions**, solo la fase 1 en este sprint:

| Fase | Contenido | Credenciales | Decisión |
|---|---|---|---|
| 1 | Frontend: `oxlint`, `vitest run` (con `--reporter=github-actions`), `npm run build` y `npm audit`; Playwright; backend: Bandit y `pip-audit` | No necesita secretos | **Se implementa en el Sprint 3** |
| 2 | Pruebas de pytest del backend | Necesita las credenciales de Supabase como secretos del repositorio | **Se pospone**: se reevalúa al terminar todos los sprints |

Motivo de posponer la fase 2: las pruebas del backend corren contra la base real de Supabase con la cuenta de pruebas y duran unos 7 minutos. Ejecutarlas en GitHub exigiría tres cuidados que no caben en este sprint: un grupo de `concurrency` para que no corran dos a la vez (`test_sesiones` y `test_mfa` borran las sesiones de la cuenta), una cuenta de pruebas exclusiva para CI distinta de la que se usa a mano, y limitar la ejecución a los Pull Request hacia `main` para cuidar los minutos gratuitos de GitHub Actions. Mientras tanto, los pytest se siguen ejecutando localmente antes de cada Pull Request.

## 5. Resultados

| Fecha | Prueba | Resultado | Observaciones |
|---|---|---|---|
| 2026-10-20 | pytest, suite completa del backend | 313 pasan; cobertura total de 98 % | Incluye las pruebas de HU-012 y HU-013 contra la base real; 20 min |
| 2026-10-20 | Vitest, frontend | 72 pasan | Incluye las pruebas de re-optimización, entregas, incidentes y mapa de rutas; `npm run build` sin errores |
| 2026-10-20 | Benchmark de re-optimización (150 pedidos, 15 vehículos) | 14.5 a 21.6 s con la reserva de guardado, límite de 30 s | Máquina de desarrollo |
| 2026-10-20 | Re-optimización en Render (150 pedidos, 15 vehículos, 5 corridas) | 27.1 a 27.2 s en el servidor y 29.0 a 29.1 s desde fuera; todas dentro de 30 s | Servicio gratuito de Render; margen corto, ver la sección 8.1 de `02 Implementación de la re-optimización` |
| 2026-10-20 | Benchmark de generación con hora punta (150 pedidos, 15 vehículos, 10 corridas) | Mediana de 12.8 s, percentil 95 de 20.2 s y máximo de 21.1 s | Límite de 45 s (RN-015); equipo de desarrollo |
| 2026-10-20 | Benchmark de re-optimización con hora punta y presupuesto de 25 s (3 semillas) | 17.9 a 22.8 s con la reserva de guardado | Límite de 30 s (RN-012); falta medir en Render |

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: pirámide de pruebas según el material del docente, decisión de no usar MSW, Playwright y la fase 1 de GitHub Actions para HT-10; fase 2 pospuesta al cierre del proyecto | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-20 | Se registran los resultados de las suites de backend y frontend y las mediciones de la re-optimización en local y en Render | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-20 | Se registran la suite completa (313 pruebas, 98 %), el frontend (72 pruebas) y los benchmarks de generación y re-optimización con hora punta | Inciso Aguilar Elizabeth Antonela |
