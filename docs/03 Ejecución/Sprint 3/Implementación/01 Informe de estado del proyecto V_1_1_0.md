# 01 Informe de Estado del Proyecto

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha del reporte** | 2026-10-20 |
| **Periodo del Informe** | 17-10-2026 – 30-10-2026 (Sprint 3 — Rutas y Visualización) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 1/5 ítems completados al 20-10-2026 (8 de 26 Story Points: HU-012, que cierra HT-07), con la re-optimización medida en Render en 27.1 a 27.2 s ([`02 Implementación de la re-optimización`](../02%20Implementaci%C3%B3n%20de%20la%20re-optimizaci%C3%B3n%20V_1_1_0.md)). Detalle por ítem en [`01 Sprint 3 Plan de ejecución y estado V_1_1_0.md`](../01%20Sprint%203%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_1_0.md). Quedó definida la estrategia de pruebas del sprint ([`03 Estrategia y resultados de pruebas`](../03%20Estrategia%20y%20resultados%20de%20pruebas%20V_1_1_0.md)). |
| **Cronograma** | Sprint iniciado el 17-10-2026; Jira lo cierra el 30-10-2026 y la fecha de inspección aún no está confirmada. Al corte van 4 de 14 días y HU-012 está completada. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_1_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_1_0.md)). Sin desviación al corte: la infraestructura (Render, Vercel, Supabase) sigue en planes gratuitos, OPEX ejecutado **USD $0.00**. |
| **Calidad** | Backend: 288 pruebas, 98 % de cobertura (96 % al cierre del Sprint 2); frontend: 60 pruebas y build sin errores. Línea base heredada del Sprint 2: Lighthouse con accesibilidad y SEO en 100 y W3C sin errores en las 8 pantallas; Lighthouse con accesibilidad y SEO en 100 y W3C sin errores en las 8 pantallas. Para el sprint: pruebas de extremo a extremo con Playwright y GitHub Actions. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Margen corto en la re-optimización de HU-012: 27.1 a 27.2 s en el servidor y 29.0 s desde fuera frente al límite de 30 s (IMP-013) | Inciso Aguilar Elizabeth Antonela | Ya se parte del plan vigente y se midió en Render; falta ampliar el margen apuntando a 25 s de presupuesto |
| Plazo corto: 26 SP en 10 días restantes y fecha de inspección sin confirmar | Inciso Aguilar Elizabeth Antonela | Orden de recorte definido en el plan de ejecución |
| Concentración del trabajo en pocas personas (IMP-005 abierto) | Inciso Aguilar Elizabeth Antonela | Responsable por ítem según Jira y checkpoint de medio sprint |

## Próximos avances

- Mapa con trazado de rutas y congestión (HU-013) y vista del conductor (HU-014).
- Responsive y WCAG 2.1 AA medidos al terminar cada pantalla (HT-09) y pruebas de extremo a extremo con GitHub Actions (HT-10).
- Heredado del Sprint 2: fijar la versión de Python en Render, reducir los viajes a la base (IMP-016) y foto del conductor con Cloudinary.

## Notas

El sistema sigue desplegado en Render (backend) y Vercel (frontend). La rama de trabajo del sprint es `sprint3`, alineada con `main` al 20-10-2026.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: informe de estado del Sprint 3 al corte del 20-10-2026 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-20 | HU-012 completada y medida en Render; se actualizan calidad y riesgos | Inciso Aguilar Elizabeth Antonela |
