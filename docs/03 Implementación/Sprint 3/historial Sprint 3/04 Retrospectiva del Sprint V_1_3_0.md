# 04 Retrospectiva del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17-10-2026 – 30-10-2026) |
| **Fecha de la retrospectiva** | Por confirmar (contenido al 22-10-2026) |
| **Versión** | 1.2.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Documento preparado el 22-10-2026** con los hechos del sprint, como propuesta de la líder del proyecto para validar con el equipo en la reunión de retrospectiva.

## ¿Qué aprendimos?

- **Medir en Render cambia las decisiones.** En una máquina de desarrollo la re-optimización tardaba 14 a 22 s; en Render, 27 s, con apenas 1 s de holgura sobre el límite. Se ajustó el presupuesto a 25 s y se midió de nuevo (22.2 s). La segunda matriz de hora punta sumó unos 4 s que solo se vieron allí (IMP-019).
- **Las pruebas en el viewport de un celular encuentran lo que las de componentes no ven.** El menú lateral ocupaba el 56 % del ancho en el celular y nadie lo había notado (IMP-021). Las capturas de pantalla ayudaron a entender la causa en minutos.
- **Una prueba que falla ante peticiones sin simular protege los cambios de contrato** (la lección de IMP-017): cada prueba de Playwright comprueba que la interfaz no pida nada que no esté simulado.
- **Los datos de prueba también fallan.** La cuenta conductora estaba bloqueada por un `token_version` desajustado (IMP-020); un conductor real habría quedado fuera.
- **Lo que no tiene datos reales se documenta como supuesto.** Los factores de hora punta se dejaron en un solo lugar del código, ajustables y declarados como supuesto en cada documento.
- **El control de versiones de los documentos y el staging necesitan cuidado:** un `git add` previo hizo que los documentos entraran en el commit equivocado, y un reemplazo masivo de nombres tocó el informe de otro sprint. Se resolvió con el verificador de enlaces.

## ¿Qué estamos haciendo bien?

- Los 26 Story Points se completaron el día 6 de 14, con cada límite del sistema medido en Render (RN-012, RN-015) y no solo en local.
- La calidad es verificable y repetible: integración continua en verde, 328 pruebas del backend con 98 % de cobertura, 89 de Vitest, 19 de Playwright, Lighthouse en 100 en accesibilidad, buenas prácticas y SEO, y W3C sin errores.
- Se aplicó la acción de la retrospectiva anterior: Lighthouse y W3C se midieron al terminar cada pantalla y quedaron automatizados.
- Cada hallazgo (la base caída, el token, el menú) se registró como impedimento con su resolución.

## ¿Qué podemos hacer mejor?

- **Personas:** el trabajo sigue concentrándose en pocas personas (IMP-005, abierto). Conviene que cada integrante lleve evidencia de su aporte en el repositorio y en la documentación.
- **Relaciones:** la aprobación de los Pull Request por un compañero en GitHub no está confirmada en todos (criterio 3 del Definition of Done).
- **Procesos:** pensar el costo en Render desde el diseño, y no al final; llevar pytest a la integración continua (fase 2) y escribir el checklist de RLS.
- **Herramientas:** el plan gratuito de Render (CPU limitada y ~2 s por petición) condiciona el rendimiento. Reutilizar matrices entre peticiones o contar con más CPU liberaría tiempo para el ACO.

### Acciones heredadas del Sprint 2: estado al 22-10-2026

| # | Acción | Responsable propuesto | Estado |
|---|---|---|---|
| 1 | Correr Lighthouse y W3C al terminar cada pantalla, no al cierre del sprint | Equipo | **Hecho** en HT-09: Lighthouse y W3C de las pantallas del sprint, automatizados con `npm run auditar` y `npm run auditar:produccion` |
| 2 | Antes de cambiar un contrato de la API, listar y actualizar todos sus consumidores en el mismo Pull Request | Quien modifique el endpoint | **Aplicado:** al ampliar las paradas y el mapa se actualizaron sus consumidores, y Playwright falla ante peticiones sin simular |
| 3 | Reducir los viajes a la base por petición (IMP-016) | Inciso Aguilar Elizabeth Antonela | Pendiente |
| 4 | Fijar la versión de Python en Render y poner topes en `requirements.txt` | Inciso Aguilar Elizabeth Antonela | Pendiente |
| 5 | Integrar cada Pull Request solo después de que un compañero lo apruebe en GitHub | Equipo | Por confirmar |
| 6 | Incluir el CRUD completo en los criterios de aceptación de cada módulo de gestión | Equipo | No aplicó: el Sprint 3 no tuvo módulos de gestión |
| 7 | GitHub Actions con pruebas y análisis estático en cada Pull Request | Guerra Lozano Keen | **Hecho (fase 1):** en verde en el Pull Request #59 y en `main`; pytest (fase 2) se pospone |
| 8 | Checklist formal de políticas RLS para toda tabla nueva | Guerra Lozano Keen | Aplicado en la práctica a `incidentes_trafico` (política permisiva y `GRANT`); falta dejarlo escrito como checklist |

### Acciones propuestas para el Sprint 4

| # | Acción | Responsable propuesto |
|---|---|---|
| 1 | Reutilizar las matrices de distancia y tiempo entre peticiones, o resolver distancia y tiempo con una sola pasada de Dijkstra | Inciso Aguilar Elizabeth Antonela |
| 2 | Calibrar los factores de hora punta con datos reales o con un criterio documentado | Equipo |
| 3 | Dejar registrada en GitHub la aprobación de cada Pull Request por un compañero | Equipo |
| 4 | Escribir el checklist de RLS y evaluar pytest en la integración continua con una base de pruebas dedicada | Guerra Lozano Keen |
| 5 | Antes de crear cuentas de conductores reales, revisar el hook de Supabase que emite `ver` en el token (IMP-020) | Inciso Aguilar Elizabeth Antonela |
| 6 | Medir en Render cada funcionalidad nueva que dependa del motor, desde su primer día | Quien la implemente |

Los responsables son una propuesta y se confirman en la reunión de retrospectiva.

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 3) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | HU-012 | Construcción de la re-optimización, el mapa por calles con horas punta, la vista del conductor, la mejora responsive, las pruebas de extremo a extremo y la integración continua; mediciones en Render y en producción; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-013, HU-014 | Revisión del sistema y búsqueda de la solución del problema de la base de datos (caída de Supabase durante la HU-012) |
| Uscuvilca Ramos Abraham Luis | HT-09, HT-10 | Pruebas del sistema como tester |
| Guerra Lozano Keen | Sin ítems en el tablero del sprint (tenía a su cargo GitHub Actions y el checklist de RLS, heredados del Sprint 1) | Revisión de la parte de re-optimización (HU-012) y apoyo en la revisión del sistema |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: estructura de la retrospectiva y seguimiento de las acciones heredadas del Sprint 2 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-22 | Se actualiza el estado de las acciones heredadas: Lighthouse y W3C por pantalla (hecho) y GitHub Actions (parcial) | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-22 | Se completan lo aprendido, lo que va bien, lo que se puede mejorar, el estado de las acciones del Sprint 2 y las acciones propuestas para el Sprint 4 | Inciso Aguilar Elizabeth Antonela |
| V_1_3_0 | 2026-10-22 | Se completa el aporte por integrante con lo declarado por la líder | Inciso Aguilar Elizabeth Antonela |
