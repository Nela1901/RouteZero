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
| **Versión** | 1.4.0 |

[← Volver al README Principal](../../../../README.md)

---

## Estado del proyecto

| Variables de control | Descripción del estado |
|---|---|
| **Alcance** | 2/5 ítems completados al 20-10-2026 (13 de 26 Story Points: HU-012, que cierra HT-07, y HU-013); la re-optimización y el mapa por calles con congestión por horas punta están medidos en Render; HU-014 (vista del conductor) está implementada y probada, a falta de medirla en Render; falta Lighthouse y W3C de las pantallas del mapa y del conductor ([`02 Implementación de la re-optimización`](../02%20Implementaci%C3%B3n%20de%20la%20re-optimizaci%C3%B3n%20V_1_3_0.md)). Detalle por ítem en [`01 Sprint 3 Plan de ejecución y estado V_1_4_0.md`](../01%20Sprint%203%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_4_0.md). Quedó definida la estrategia de pruebas del sprint ([`03 Estrategia y resultados de pruebas`](../03%20Estrategia%20y%20resultados%20de%20pruebas%20V_1_4_0.md)). |
| **Cronograma** | Sprint iniciado el 17-10-2026; Jira lo cierra el 30-10-2026 y la fecha de inspección aún no está confirmada. Al corte van 4 de 14 días y HU-012 está completada. |
| **Costos** | Presupuesto estimado académico: **USD $10,304.00** (ver [`04 Presupuesto del proyecto V_1_1_0.md`](../../../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_1_0.md)). Sin desviación al corte: la infraestructura (Render, Vercel, Supabase) sigue en planes gratuitos, OPEX ejecutado **USD $0.00**. |
| **Calidad** | Backend: 328 pruebas, 98 % de cobertura (96 % al cierre del Sprint 2); frontend: 88 pruebas y build sin errores. Línea base heredada del Sprint 2: Lighthouse con accesibilidad y SEO en 100 y W3C sin errores en las 8 pantallas; pendiente repetirlos en la pantalla del mapa. Para el sprint: pruebas de extremo a extremo con Playwright y GitHub Actions. |

## Riesgos

| Riesgo | Responsable | Mitigación |
|---|---|---|
| Costo de la matriz de hora punta en Render (IMP-013): las matrices pasan de unos 9 a unos 13 s y el ACO de la re-optimización solo hace 2 a 3 iteraciones | Inciso Aguilar Elizabeth Antonela | La re-optimización cumple (22.2 s en el servidor, 24.0 s desde fuera) y parte del plan vigente, por lo que no empeora; mejora posible: reutilizar matrices entre peticiones o un plan con más CPU |
| Cuenta de conductor rechazada por un desajuste de `token_version` (hallazgo de HU-014): un conductor real con ese desajuste quedaría bloqueado | Inciso Aguilar Elizabeth Antonela | Restablecido en la cuenta de prueba; revisar el hook de Supabase antes de crear cuentas de conductores reales |
| Plazo corto: 26 SP en 10 días restantes y fecha de inspección sin confirmar | Inciso Aguilar Elizabeth Antonela | Orden de recorte definido en el plan de ejecución |
| Concentración del trabajo en pocas personas (IMP-005 abierto) | Inciso Aguilar Elizabeth Antonela | Responsable por ítem según Jira y checkpoint de medio sprint |

## Próximos avances

- Vista del conductor (HU-014): vínculo conductor–usuario, ruta propia, entregas y alertas de tráfico.
- Medir en Render la vista del conductor (HU-014) tras el despliegue.
- Lighthouse y W3C de las pantallas del mapa (HU-013) y del conductor (HU-014).
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
| V_1_2_0 | 2026-10-20 | Se agrega el avance de HU-013, el nuevo margen de la re-optimización y los próximos pasos | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-20 | HU-013 completada; se actualizan calidad, riesgos (costo de la segunda matriz en Render) y próximos avances | Inciso Aguilar Elizabeth Antonela |
| V_1_4_0 | 2026-10-20 | Se agrega el avance de HU-014, el hallazgo del token del conductor y los próximos pasos | Inciso Aguilar Elizabeth Antonela |
