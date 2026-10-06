# 03 Revisión del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03-10-2026 – 16-10-2026) |
| **Fecha de la revisión** | 2026-10-16 (prevista); contenido preparado con el estado al 2026-10-06 |
| **Versión** | 1.4.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Estado del documento.** El contenido refleja lo verificado al 06-10-2026. Lo que cambie hasta la inspección del 16-10-2026 se registra en una nueva versión.

## Historias de Usuario completadas en este Sprint

Compromiso del sprint: 6 ítems y 41 Story Points. Detalle y evidencias en [`01 Sprint 2 Plan de ejecución y estado`](../01%20Sprint%202%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_4_0.md).

| ID | Historia | Épica | SP | Estado |
|---|---|---|---|---|
| HU-009 | Registrar conductor | EP-04 Gestión de Personas | 3 | Completada |
| HU-010 | Registrar cliente con preferencias de entrega | EP-04 Gestión de Personas | 2 | Completada |
| HU-011 | Generar rutas optimizadas para la jornada | EP-05 Optimización de Rutas | 13 | Completada |
| HT-06 | Pruebas unitarias del módulo de personas | EP-04 Gestión de Personas | 8 | Completada |
| HT-07 | Implementar motor de optimización ACO | EP-05 Optimización de Rutas | 2 | **Parcial** |
| HT-08 | Diseñar arquitectura escalable | EP-05 Optimización de Rutas | 13 | Completada |

**Resultado: 39 de 41 Story Points (95 %).** HT-07 queda parcial: su segundo escenario (re-optimización en ≤ 30 s ante un incidente) depende de HU-012, que pertenece al Sprint 3.

## Demostración del trabajo completado

Orden previsto para la demostración (máximo 10 minutos):

1. **Inicio de sesión con MFA** y vista por rol (el Operador no ve Flota).
2. **Conductores y Clientes**: registro con consentimiento explícito (RN-013), vencimiento de licencia y punto de referencia dentro de la zona de Huancayo (RN-007).
3. **Pedidos**: listado paginado y mapa con los pedidos pendientes.
4. **Rutas**: generar rutas en borrador para una jornada, revisar kilómetros, litros y CO₂, y confirmar (los pedidos pasan a ASIGNADO y los recursos quedan comprometidos). Mostrar un caso con pedidos sin cobertura, con su motivo y sugerencia.
5. **Evidencias de calidad**: cobertura, medición en Render, Lighthouse y validación W3C.

### Resultados medidos

| Criterio | Meta | Resultado |
|---|---|---|
| Generación de rutas (150 pedidos, 15 vehículos) en Render gratuito | ≤ 45 s | **29.1 s**, 150 de 150 pedidos atendidos |
| Memoria en Render (512 MB) | dentro del límite | pico de 199 a 210 MB |
| Carga con 1,000 pedidos (percentil 95) | ≤ 2 s | 1.06 a 1.14 s |
| Cobertura de pruebas del backend | ≥ 80 % | 96 % |
| Seguridad | 0 críticas | Bandit sin hallazgos altos, `pip-audit` y `npm audit` sin vulnerabilidades |
| Lighthouse (producción, 06-10-2026) | ≥ 90 | Accesibilidad 100 y SEO 100 en las 8 pantallas, móvil y escritorio; buenas prácticas 96-100; **rendimiento 85-100** |
| Validación W3C (validador Nu, DOM renderizado) | sin errores | 0 errores y 0 avisos en las 8 pantallas |

**Salvedad sobre Lighthouse:** el rendimiento queda por debajo de 90 en Mapa (88-89) y en Pedidos (85, escritorio). La causa medida es la latencia de la API en Render gratuito (cerca de 1 s por petición); el hilo principal no se bloquea (TBT 0 ms) ni hay desplazamientos de diseño (CLS 0). Está registrado como IMP-016 en el [Registro de Impedimentos](02%20Registro%20de%20Impedimentos%20V_1_1_0.md).

### Trabajo adicional al compromiso

Ver sección 3 del plan de ejecución: corrección del filtro y del registro de Flota, motor de rutas sobre calles reales de OpenStreetMap, vencimientos de SOAT, revisión técnica y licencia, ayudas en los formularios, interfaz adaptable y control de acceso por rol en el menú. La auditoría de Lighthouse encontró además una regresión real (el mapa fallaba tras paginar los pedidos), corregida con su prueba.

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 2) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | HU-011, HT-08 | Construcción del motor de rutas, la red vial, la arquitectura escalable y las pruebas de rendimiento y carga; documentación del sprint |
| Guerra Lozano Keen | HU-009, HT-06 | Revisión de la HU-009 |
| Uscuvilca Ramos Abraham Luis | HU-010 | Realizó la HU-010 |
| Espinoza Tiza Yago Imanol | HT-07 | Apoyo en la HU-011 |

**Nota de proceso:** el equipo colaboró, pero los commits y push del repositorio se hacen desde una sola cuenta de GitHub, la de la líder del proyecto, para agilizar la integración. Por eso el historial de Git no refleja por sí solo la autoría de cada integrante y este cuadro es la referencia de quién aportó en qué. Los cuatro integrantes figuran como Contributors del repositorio en GitHub. Además, las revisiones se hacen en persona, desde la computadora de la líder, cuando el equipo trabaja junto en clase.

## Pendientes

- **HT-07, escenario 2** (re-optimización en ≤ 30 s): pasa al Sprint 3 junto con HU-012.
- **Definition of Done, criterio 3** (ya no pendiente): **cumplido el 06-10-2026**, el Pull Request #45 fue aprobado en GitHub por YagoEspinoza el 06-10-2026 antes de integrarse. Los Pull Request anteriores se revisaron en persona, sin constancia en GitHub.
- Rendimiento de las pantallas con datos (IMP-016) y velocidad del cálculo en Render gratuito (IMP-013): abiertos.
- Foto del conductor con Cloudinary (trabajo adicional, no comprometido en el sprint).
- Heredado del Sprint 1: GitHub Actions para pruebas y análisis estático en cada Pull Request.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: estructura de la revisión con el alcance comprometido; el resto se completa al cierre | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-06 | Se completan el estado de los ítems (39/41 SP), los resultados medidos, el aporte por integrante y los pendientes | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-06 | Se precisa que la revisión de código es presencial (criterio 3 del Definition of Done) | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-06 | Se deja constancia de que los cuatro integrantes figuran como Contributors del repositorio en GitHub | Inciso Aguilar Elizabeth Antonela |
| V_1_4_0 | 2026-10-06 | El criterio 3 del Definition of Done pasa de pendiente a cumplido con la aprobación del Pull Request #45 por YagoEspinoza | Inciso Aguilar Elizabeth Antonela |
