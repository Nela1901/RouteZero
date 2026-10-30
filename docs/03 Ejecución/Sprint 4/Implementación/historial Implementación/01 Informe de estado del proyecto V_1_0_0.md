# 01 Informe de Estado del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha del reporte** | 2026-10-23 |
| **Periodo del Informe** | 22-10-2026 – 13-11-2026 (Sprint 4 — Sostenibilidad y Cierre) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | **5/5 ítems completados al 23-10-2026 (18 de 18 Story Points)**: HU-015, HU-016, HU-017, HT-11 y HT-12. Detalle por ítem en [`01 Sprint 4 Plan de ejecución y estado`](../../historial%20Sprint%204/01%20Sprint%204%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_3_0.md) y en [`02 Implementación de la sostenibilidad`](../../historial%20Sprint%204/02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_2_0.md). |
| **Cronograma** | Sprint iniciado el 22-10-2026 en Jira, que lo cierra el 13-11-2026; la fecha de inspección aún no está confirmada. Al corte (23-10-2026) van 2 de 23 días y los 18 SP están completados: queda margen para las pruebas de aceptación, la documentación técnica y la preparación de la sustentación final, que son parte de la meta del sprint en Jira, y para la actividad de cierre del proyecto (SonarQube Cloud, OWASP Top 10 2025, WCAG 2.2 y usabilidad). |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_1_0.md`](../../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_1_0.md)). Sin desviación al corte: la infraestructura (Render, Vercel, Supabase) sigue en planes gratuitos, OPEX ejecutado **USD $0.00**. Las dos bibliotecas nuevas (`fpdf2` y `pypdf`) son de código abierto. |
| **Calidad** | Backend: 359 pruebas, 98 % de cobertura total y 100 % en el módulo nuevo `sostenibilidad`; frontend: 99 pruebas de Vitest y 26 de Playwright. Integración continua de GitHub Actions en verde en `main`. Pantalla Sostenibilidad: Lighthouse con accesibilidad, buenas prácticas y SEO en 100 y rendimiento de 95 (móvil) a 99 (escritorio), y W3C sin errores. Las 17 consultas críticas de la base tardan 42 ms o menos en el servidor. `npm audit` y `pip-audit` sin vulnerabilidades y Bandit sin hallazgos. En Render: dashboard 2.4 s, plan de compensación 2.3 s y reporte PDF de 30 días 7.5 s. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Precio del combustible, meta mensual de CO₂ y árboles por tonelada son supuestos sin datos reales de la empresa (IMP-024) | Inciso Aguilar Elizabeth Antonela | Declarados como supuestos y ajustables por variable de entorno; validarlos con Andina Reparto antes de usar las cifras para decidir |
| Los vehículos ya registrados no tienen precio de compra ni vida útil: el costo del ciclo de vida del reporte los muestra como «sin dato» | Inciso Aguilar Elizabeth Antonela | El formulario de Flota ya pide los dos datos; falta cargarlos para los vehículos reales |
| El reporte PDF de un mes completo tarda unos 7.5 s en Render por su CPU de 0.1 (IMP-026) | Inciso Aguilar Elizabeth Antonela | Aceptable para una descarga manual; la pantalla muestra el avance y el reporte lista como máximo 300 rutas |
| Concentración del trabajo en pocas personas (IMP-005 abierto) | Inciso Aguilar Elizabeth Antonela | Responsable por ítem según Jira; el aporte de cada integrante se documenta en la revisión y la retrospectiva |
| Cambios de esquema que solo se pueden aplicar a mano en Supabase (IMP-023) | Inciso Aguilar Elizabeth Antonela | Cada cambio va en un `.sql` idempotente de `backend/scripts/` que se ejecuta antes de desplegar |
| Latencia de Render y de la base remota (IMP-013, IMP-016) y costo de la matriz de hora punta (IMP-019), heredados | Inciso Aguilar Elizabeth Antonela | Documentados como limitaciones del plan gratuito; reutilizar matrices entre peticiones o más CPU las aliviaría |

## Próximos avances

- Pruebas de aceptación de los escenarios de cada historia por un integrante distinto de quien la implementó.
- Documentación técnica del proyecto (las carpetas `04 Seguimiento_Control` y `05 Cierre` siguen sin contenido) y preparación de la sustentación final.
- Actividad de cierre del proyecto, al terminar todos los sprints: SonarQube Cloud sobre backend y frontend, mapeo a OWASP Top 10 2025, revisión de WCAG 2.2 y evaluación de usabilidad (escala SUS en positivo y heurísticas de Nielsen).
- Reunión de retrospectiva con el equipo para validar las acciones propuestas, y revisión del sprint en la fecha que se confirme.
- Medir Lighthouse sobre la pantalla Sostenibilidad ya desplegada en Vercel y cargar el precio de compra y la vida útil de los vehículos reales.
- Heredado: reutilizar matrices entre peticiones y reducir los viajes a la base (IMP-016, IMP-019), fijar la versión de Python en Render, escribir el checklist de RLS, evaluar pytest en la integración continua (fase 2) y la foto del conductor con Cloudinary.

## Notas

El sistema sigue desplegado en Render (backend) y Vercel (frontend), con los tres endpoints de sostenibilidad y la pantalla nueva ya en producción. La rama de trabajo del sprint es `sprint4`, alineada con `main` al 23-10-2026. Los Pull Request del sprint son el #62 a #65; el criterio 3 del Definition of Done (aprobación de un compañero) se cumplió en el #64, aprobado por Yago Espinoza y Keen Guerra.

---

[← Volver al README Principal](../../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-23 | Versión inicial: informe de estado del Sprint 4 con el sprint completo (18 de 18 SP) al corte del 23-10-2026 | Inciso Aguilar Elizabeth Antonela |
