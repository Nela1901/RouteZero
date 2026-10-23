# 03 Revisión del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17-10-2026 – 30-10-2026) |
| **Fecha de la revisión** | Por confirmar (contenido al 22-10-2026) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

> **Documento preparado el 22-10-2026**, con el sprint completo y antes de la inspección, cuya fecha aún no está confirmada. Se actualiza si algo cambia hasta entonces.

## Historias de Usuario completadas en este Sprint

Compromiso del sprint: 5 ítems y 26 Story Points. Detalle y evidencias en [`01 Sprint 3 Plan de ejecución y estado`](../01%20Sprint%203%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_6_0.md).

| ID | Historia | Épica | SP | Estado |
|---|---|---|---|---|
| HU-012 | Re-optimizar rutas ante evento de cambio operativo | EP-05 Optimización de Rutas | 8 | Completada |
| HU-013 | Visualizar rutas optimizadas en mapa interactivo | EP-06 Visualización de Rutas | 5 | Completada |
| HU-014 | Visualizar ruta asignada en modo conductor | EP-06 Visualización de Rutas | 3 | Completada |
| HT-09 | Implementar diseño responsive y cumplimiento WCAG 2.1 AA | EP-06 Visualización de Rutas | 5 | Completada |
| HT-10 | Pruebas de integración del mapa interactivo | EP-06 Visualización de Rutas | 5 | Completada |

**Resultado: 26 de 26 Story Points (100 %).** HT-07 del Sprint 2, que había quedado parcial, se cierra con HU-012.

## Demostración del trabajo completado

Orden previsto para la demostración (máximo 10 minutos):

1. **Inicio de sesión** y vista por rol: el Operador no ve Flota ni Conductores.
2. **Mapa de rutas** (HU-013): recorridos por las calles de Huancayo, paradas numeradas con su estado y el tiempo de cada tramo. Cambiar la hora de la congestión a las 8:30 para ver las vías en amarillo por hora punta.
3. **Incidente y re-optimización** (HU-012): registrar un incidente en Av. Ferrocarril (la vía pasa a rojo), agregar un pedido urgente, re-optimizar y confirmar el borrador. El resumen informa el tiempo (límite de 30 s) y los pedidos integrados.
4. **Vista del conductor** en el celular (HU-014): su ruta, la siguiente parada, las alertas «en tu ruta» y el registro de una entrega.
5. **Evidencias de calidad**: integración continua en verde, 328 pruebas del backend con 98 % de cobertura, Playwright, Lighthouse y W3C.

Preparación: calentar Render unos minutos antes (el servicio gratuito tarda entre 30 y 45 s en despertar), dejar los datos de demostración (`datos_demo.sql`) y generar y confirmar las rutas de la jornada. La re-optimización tarda cerca de 24 s en Render: conviene explicarla mientras se calcula.

### Resultados medidos

| Criterio | Meta | Resultado |
|---|---|---|
| Re-optimización (150 pedidos, 15 vehículos, hora punta) en Render gratuito | ≤ 30 s (RN-012) | **22.2 s** en el servidor y **24.0 s** medidos desde fuera |
| Generación de rutas (150 pedidos, 15 vehículos) en Render gratuito | ≤ 45 s (RN-015) | **30.0 s**, 150 de 150 pedidos atendidos |
| Vista del conductor en Render | — | 3.8 s la primera petición y 2.6 s desde la caché |
| Mapa en Render (14 rutas) | — | 9.3 s la primera carga y 2.6 s desde la caché |
| Cobertura de pruebas del backend | ≥ 80 % | **98 %** (328 pruebas) |
| Pruebas del frontend | — | 89 de Vitest y 19 de Playwright (escritorio y móvil) |
| Integración continua (GitHub Actions) | en verde | Pull Request #59 y la integración a `main`, con los tres trabajos |
| Seguridad | 0 críticas | Bandit sin hallazgos altos, `pip-audit` y `npm audit` sin vulnerabilidades |
| Lighthouse en producción (22-10-2026) | ≥ 90 | Accesibilidad, buenas prácticas y SEO en **100**; rendimiento de **91 a 98** |
| Validación W3C (validador Nu, DOM renderizado) | sin errores | 0 errores y 0 avisos en las 5 pantallas del sprint |

**Salvedades:**

- Los factores de congestión por hora punta (Av. Ferrocarril ×1.8, Av. Giráldez ×1.6 y Calle Real ×1.3) son **supuestos sin datos reales de tráfico**; quedan ajustables en el código.
- La segunda matriz de hora punta sube el cálculo de las matrices de unos 9 a unos 13 s en Render y el ACO de la re-optimización hace 2 a 3 iteraciones (IMP-019). El resultado nunca es peor que el plan vigente, pero aporta poca mejora adicional en el plan gratuito.
- La validación W3C usa el servicio público con datos sintéticos, por lo que no corre en la integración continua.

### Trabajo adicional al compromiso

Entre otros: cancelar un pedido ya asignado, panel de incidentes de tráfico, corrección del diseño responsive (menú lateral colapsado en el celular y panel del mapa plegable), aviso de carga del mapa, auditoría repetible con `npm run auditar` y `npm run auditar:produccion`, scripts de medición en Render, y actualización de dependencias para dejar `npm audit` en 0.

## Pendientes

- **Foto del conductor con Cloudinary**: no estaba comprometida; sigue pendiente.
- **Rendimiento en Render**: reutilizar las matrices entre peticiones o reducir los viajes a la base por petición (IMP-016, IMP-019).
- **Integración continua, fase 2**: las pruebas de pytest contra Supabase se reevalúan al cerrar todos los sprints.
- **Vínculo conductor-usuario**: se hace por correo; no hay pantalla para asignarlo a mano.
- **Calibración** de los factores de hora punta con datos reales.
- **Checklist formal de políticas RLS** y **versión de Python fijada en Render** (acciones heredadas).
- **Aprobación de los Pull Request por un compañero** en GitHub: por confirmar (criterio 3 del Definition of Done).

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 3) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | HU-012 | Construcción de la re-optimización, el mapa por calles con horas punta, la vista del conductor, la mejora responsive, las pruebas de extremo a extremo y la integración continua; mediciones en Render y en producción; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-013, HU-014 | Revisión del sistema y búsqueda de la solución del problema de la base de datos (caída de Supabase durante la HU-012) |
| Uscuvilca Ramos Abraham Luis | HT-09, HT-10 | Pruebas del sistema como tester |
| Guerra Lozano Keen | Sin ítems en el tablero del sprint (tenía a su cargo GitHub Actions y el checklist de RLS, heredados del Sprint 1) | Revisión de la parte de re-optimización (HU-012) y apoyo en la revisión del sistema |

**Nota de proceso:** el equipo colaboró, pero los commits y push del repositorio se hacen desde una sola cuenta de GitHub, la de la líder del proyecto, para agilizar la integración. Por eso el historial de Git no refleja por sí solo la autoría de cada integrante y este cuadro es la referencia de quién aportó en qué. Las revisiones se hacen en persona, desde la computadora de la líder, cuando el equipo trabaja junto en clase.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: estructura de la revisión con el alcance comprometido; el resto se completa al cierre | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-22 | Se completan el resultado (26 de 26 SP), la demostración de 10 minutos, los resultados medidos, el trabajo adicional y los pendientes; el aporte por integrante queda por completar | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-10-22 | Se completa el aporte por integrante con lo declarado por la líder | Inciso Aguilar Elizabeth Antonela |
