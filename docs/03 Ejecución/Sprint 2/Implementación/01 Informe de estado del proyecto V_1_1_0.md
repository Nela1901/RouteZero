# 01 Informe de Estado del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha del reporte** | 2026-10-05 |
| **Periodo del Informe** | 03-10-2026 – 16-10-2026 (Sprint 2 — Personas y Algoritmo ACO) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 3/6 ítems completados al 05-10-2026 (13 de 41 Story Points): HU-009 (conductores), HU-010 (clientes con preferencias de entrega) y HT-06 (pruebas del módulo de personas). La épica EP-04 queda cerrada. Pendiente la épica EP-05: motor de optimización ACO y generación de rutas (HU-011, HT-07, HT-08; 28 SP). Trabajo adicional: vencimientos de licencia, SOAT y revisión técnica, ayudas en formularios, interfaz adaptable al ancho disponible y correcciones de Flota. Detalle en [`01 Sprint 2 Plan de ejecución y estado V_1_2_0.md`](../01%20Sprint%202%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_2_0.md). |
| **Cronograma** | Sprint iniciado el 03-10-2026; inspección el 16-10-2026. Sin atraso al corte: los primeros días se dedicaron a cerrar observaciones del sprint anterior y a la documentación de arranque. Checkpoint de medio sprint previsto para el 10-10-2026. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_0_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_0_0.md)). Sin desviación al corte: la infraestructura (Render, Vercel, Supabase) sigue en planes gratuitos, OPEX ejecutado **USD $0.00**. |
| **Calidad** | 100 pruebas automatizadas con pytest en el backend y 96 % de cobertura (autenticación, flota, conductores, clientes, pedidos y auditoría); 5 pruebas de frontend con Vitest (solo MFA). Se corrigió `pytest.ini`, que no medía `src.conductores`. Pendiente para el sprint: Bandit, pip-audit y npm audit, y la primera auditoría de Lighthouse (RSK-007). |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Complejidad del motor de optimización ACO (HU-011, HT-07 y HT-08 suman 28 SP en Jira) en dos semanas | Inciso Aguilar Elizabeth Antonela | Versión mínima correcta primero (capacidad y ventanas de tiempo), afinación después, y medición de rendimiento desde el primer día |
| Disponibilidad limitada del equipo (RSK-005, IMP-005 abierto) | Inciso Aguilar Elizabeth Antonela | Dueño explícito por módulo en Jira y checkpoint de medio sprint el 10-10-2026 |
| Story Points de Jira distintos a la documentación en HT-06, HT-07, HT-08 y HT-10 (ver sección 2.1 del plan de ejecución) | Inciso Aguilar Elizabeth Antonela | Confirmar con el equipo cuál es la estimación vigente y alinear Jira y [`01 Transformando a ágil`](../../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md) |

## Próximos avances

- Motor de optimización ACO y generación de rutas (EP-05), con tablas `rutas` y `ruta_pedidos`.
- Foto del conductor con Cloudinary (trabajo adicional, después del motor de optimización).
- Motor de optimización ACO (HT-07), generación de rutas (HU-011) y arquitectura escalable con pruebas de carga (HT-08).
- Reglas de negocio pendientes que dependen de conductores y rutas (RN-002/003, RN-004, RN-005, RN-006, RN-008, RN-009, RN-012, RN-015).
- Heredado del Sprint 1: pruebas del frontend para Flota y Pedidos, Lighthouse y validación W3C, GitHub Actions para pruebas y análisis estático en cada Pull Request.

## Notas

El sistema sigue desplegado en Render (backend) y Vercel (frontend). Las correcciones de Flota de este informe están en la rama de trabajo y se publicarán con el siguiente Pull Request.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: informe de estado del Sprint 2 al inicio del sprint | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-05 | Se actualiza el estado: HU-009, HU-010 y HT-06 completadas (13/41 SP, EP-04 cerrada), cobertura real de 96 % con 100 pruebas | Inciso Aguilar Elizabeth Antonela |
