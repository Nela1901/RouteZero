# 01 Informe de Estado del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha del reporte** | 2026-10-06 |
| **Periodo del Informe** | 03-10-2026 – 16-10-2026 (Sprint 2 — Personas y Algoritmo ACO) |
| **Versión** | 1.4.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 39 de 41 Story Points completados al 05-10-2026 (HU-009, HU-010, HU-011, HT-06 y HT-08); **HT-07 (2 SP) parcial**: su escenario de re-optimización en ≤ 30 s depende de HU-012 (Sprint 3). Entregado: gestión de conductores y clientes, red vial propia de Huancayo con datos de OpenStreetMap, motor de optimización ACO, generación de rutas en borrador con confirmación y descarte, módulos independientes y API escalable. Trabajo adicional: vencimientos de licencia, SOAT y revisión técnica, ayudas en formularios, interfaz adaptable y exclusión de recursos ya comprometidos. Detalle en [`01 Sprint 2 Plan de ejecución y estado V_1_3_0.md`](../01%20Sprint%202%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_3_0.md). |
| **Cronograma** | El núcleo del sprint quedó completo 11 días antes de la inspección (16-10-2026). Lo que queda para el cierre: revisión y retrospectiva del sprint y foto del conductor (trabajo adicional). La auditoría de Lighthouse y la validación W3C se hicieron el 06-10-2026. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_0_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)). Sin desviación al corte: la infraestructura (Render, Vercel, Supabase) sigue en planes gratuitos, OPEX ejecutado **USD $0.00**. |
| **Calidad** | 96 % de cobertura en el backend con más de 170 pruebas de pytest contra la base real (más pruebas de rendimiento y carga que se ejecutan aparte) y 17 pruebas de Vitest. Bandit sin hallazgos de severidad alta, `pip-audit` sin vulnerabilidades y `npm audit` en 0. Rendimiento medido en Render gratuito: 29.1 s por generación con 150 pedidos y 15 vehículos (límite 45 s), pico de memoria de 199 a 210 MB de 512 MB; percentil 95 de 1.06 a 1.14 s con 1,000 pedidos (límite 2 s). Lighthouse en producción (06-10-2026): accesibilidad 100 y SEO 100 en las 8 pantallas (móvil y escritorio), rendimiento 85-100 (Mapa y Pedidos por debajo de 90 por la latencia de la API en Render gratuito); W3C con 0 errores y 0 avisos. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Rendimiento limitado de Render gratuito (0.1 de CPU): las matrices por calles tardan 8.3 a 8.8 s (frente a ~1 s en desarrollo) y el ACO hace 8 a 9 iteraciones (frente a ~50), por lo que la solución es válida pero menos pulida; el tiempo total se mantiene en 29.1 s | Inciso Aguilar Elizabeth Antonela | Reservar tiempo para guardar dentro del presupuesto (hecho); evaluar reducir el cálculo de matrices o un plan con más CPU antes de la sustentación |
| Disponibilidad limitada del equipo (RSK-005, IMP-005 abierto) | Inciso Aguilar Elizabeth Antonela | Dueño explícito por módulo en Jira y checkpoint de medio sprint adelantado al 06-10-2026 |
| Story Points de Jira distintos a la documentación en HT-06, HT-07, HT-08 y HT-10 (ver sección 2.1 del plan de ejecución) | Inciso Aguilar Elizabeth Antonela | Confirmar con el equipo cuál es la estimación vigente y alinear Jira y [`01 Transformando a ágil`](../../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md) |

## Próximos avances

- Sprint 3: re-optimización ante incidentes (HU-012, que cierra HT-07), mapa interactivo de rutas (HU-013), vista del conductor (HU-014) y congestión en Av. Ferrocarril, Av. Giráldez y Calle Real, para la que el grafo ya guarda el nombre de cada tramo.
- Foto del conductor con Cloudinary (trabajo adicional, después del motor de optimización).
- Motor de optimización ACO (HT-07), generación de rutas (HU-011) y arquitectura escalable con pruebas de carga (HT-08).
- Reglas de negocio pendientes que dependen de conductores y rutas (RN-002/003, RN-004, RN-005, RN-006, RN-008, RN-009, RN-012, RN-015).
- Heredado del Sprint 1: pruebas del frontend para Flota y Pedidos, GitHub Actions para pruebas y análisis estático en cada Pull Request.

## Checkpoint de medio sprint

Acción heredada del Sprint 1: cada integrante informa su avance y sus bloqueos a mitad del sprint. Se adelantó del 10-10-2026 al **06-10-2026**, porque el núcleo del sprint ya estaba completo. El cuadro recoge el estado verificable de cada ítem asignado en Jira, el aporte que el equipo declaró y los bloqueos y próximos pasos que constan en los documentos del sprint (Registro de Impedimentos y plan de ejecución). No se registraron bloqueos nuevos de los integrantes fuera de los ya listados en el Registro de Impedimentos.

| Integrante | Ítems en Jira | Avance verificado al 06-10-2026 | Aporte declarado por el equipo | Bloqueos y próximos pasos |
|---|---|---|---|---|
| Inciso Aguilar Elizabeth Antonela | HU-011, HT-08 | Ambas completadas (motor de rutas, arquitectura escalable) | Motor, red vial, pruebas de rendimiento y carga, documentación | Sin bloqueos para el cierre; siguen abiertos IMP-013 (CPU de Render) e IMP-016 (latencia de la API). Próximo: datos y ensayo de la demostración |
| Guerra Lozano Keen | HU-009, HT-06 | Ambas completadas (módulo y pruebas de conductores) | Revisión de la HU-009 | Sin bloqueos registrados. Próximo: GitHub Actions y checklist de RLS (acciones heredadas del Sprint 1 a su cargo), en el Sprint 3 |
| Uscuvilca Ramos Abraham Luis | HU-010 | Completada (registro de clientes con preferencias de entrega) | Realizó la HU-010 | Sin bloqueos registrados. Próximo: ítems del Sprint 3 según Jira |
| Espinoza Tiza Yago Imanol | HT-07 | Parcial (escenario 1 verificado; el escenario 2 depende de HU-012, Sprint 3) | Apoyo en la HU-011 | Bloqueo de calendario: el escenario 2 de HT-07 solo puede cerrarse con HU-012. Próximo: cerrar HT-07 junto con HU-012 en el Sprint 3 |

Los commits salen de una sola cuenta de GitHub y la revisión de código es presencial (ver criterio 3 del Definition of Done en el plan de ejecución), por lo que el historial de Git no muestra la autoría de cada integrante.

## Notas

El sistema sigue desplegado en Render (backend) y Vercel (frontend). Las correcciones de Flota de este informe están en la rama de trabajo y se publicarán con el siguiente Pull Request.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: informe de estado del Sprint 2 al inicio del sprint | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-05 | Se actualiza el estado: HU-009, HU-010 y HT-06 completadas (13/41 SP, EP-04 cerrada), cobertura real de 96 % con 100 pruebas | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-05 | Se actualiza el estado al completar el motor de rutas: 39/41 SP, medición en Render y resultados de calidad y seguridad | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-06 | Se registran la auditoría de Lighthouse y la validación W3C en producción y se retiran de los pendientes | Inciso Aguilar Elizabeth Antonela |
| V_1_4_0 | 2026-10-06 | Se agrega el cuadro del checkpoint de medio sprint con el estado verificable, los bloqueos y los próximos pasos de cada integrante; el checkpoint se adelanta al 06-10-2026 | Inciso Aguilar Elizabeth Antonela |
