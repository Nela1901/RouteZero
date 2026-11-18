# Revisión del sprint

[← Volver al README principal](../../../README.md)

**Nombre del Proyecto:** RouteZero — Optimizador de rutas sostenibles (empresa ficticia Andina Reparto S.A.C., Huancayo)

**Líder del Proyecto:** Inciso Aguilar Elizabeth Antonela

## Historias de Usuario completadas en este Sprint

Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026): 5 ítems y 18 Story Points, todos completados (**18 de 18, 100 %**). Cada ítem cumple el Definition of Done del proyecto: criterios de aceptación ejecutados y aprobados, cobertura mayor o igual al 80 %, análisis estático sin hallazgos críticos, despliegue en Render y Vercel, y integración a `main` por Pull Request. El detalle por ítem y las evidencias están en el [plan de ejecución](Plan%20y%20documentos%20t%C3%A9cnicos/01%20Sprint%204%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_5_0.md) y en la [implementación de la sostenibilidad](Plan%20y%20documentos%20t%C3%A9cnicos/02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_4_0.md).

| Código | Título | SP | Criterios de aceptación verificados | Pull Request y commits de cierre |
|---|---|---|---|---|
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | 5 | **E1:** con jornadas registradas muestra distancia, CO₂, combustible ahorrado, cumplimiento de ventanas y ahorro en soles. **E2:** sin datos del periodo muestra ceros y el aviso. Probados en la API (`test_sostenibilidad.py`) y en pantalla (`sostenibilidad.spec.ts`) | [PR #62](https://github.com/Nela1901/RouteZero/pull/62): [`3dad699`](https://github.com/Nela1901/RouteZero/commit/3dad699) (backend) y [`ff6e2ef`](https://github.com/Nela1901/RouteZero/commit/ff6e2ef) (pantalla). Cierre con la medición en Render: [PR #64](https://github.com/Nela1901/RouteZero/pull/64), [`05aaa36`](https://github.com/Nela1901/RouteZero/commit/05aaa36) |
| HU-016 | Descargar reporte de sostenibilidad en PDF | 5 | **E1:** el PDF trae CO₂ por ruta, costo del ciclo de vida de la flota, ahorro de combustible y metas. **E2:** sin datos responde con el aviso y sugiere otro periodo, sin PDF vacío. Probados con 15 pruebas de `test_reporte_pdf.py` y de extremo a extremo | [PR #63](https://github.com/Nela1901/RouteZero/pull/63): [`f291eae`](https://github.com/Nela1901/RouteZero/commit/f291eae) (backend) y [`092d041`](https://github.com/Nela1901/RouteZero/commit/092d041) (descarga en pantalla). Cierre: [PR #64](https://github.com/Nela1901/RouteZero/pull/64), [`05aaa36`](https://github.com/Nela1901/RouteZero/commit/05aaa36) |
| HU-017 | Consultar plan de compensación de carbono | 3 | **E1:** calcula el CO₂ del periodo, los árboles necesarios, la alerta si supera la meta mensual y las alianzas de reforestación a explorar. **E2:** sin emisiones informa que faltan datos | [PR #62](https://github.com/Nela1901/RouteZero/pull/62): [`3dad699`](https://github.com/Nela1901/RouteZero/commit/3dad699) y [`ff6e2ef`](https://github.com/Nela1901/RouteZero/commit/ff6e2ef). Cierre: [PR #64](https://github.com/Nela1901/RouteZero/pull/64), [`05aaa36`](https://github.com/Nela1901/RouteZero/commit/05aaa36) |
| HT-11 | Optimizar consultas SQL aplicando principios Green Software | 3 | **E1:** las consultas críticas se ejecutan en 500 ms o menos: 17 de 17 en 42 ms o menos con un volumen de seis meses. **E2:** ninguna consulta sin índice; se agregó `idx_pedidos_creado` (listado de pedidos de 7.0 a 0.1 ms) | [PR #63](https://github.com/Nela1901/RouteZero/pull/63): [`f291eae`](https://github.com/Nela1901/RouteZero/commit/f291eae) (script `auditar_consultas.py` y migración de índices) |
| HT-12 | Pruebas de generación de reportes PDF | 2 | **E1:** con datos, el PDF es válido y se lee de vuelta con `pypdf` (emisiones, ahorro y costos). **E2:** sin datos, mensaje esperado y ningún PDF vacío | [PR #63](https://github.com/Nela1901/RouteZero/pull/63): [`f291eae`](https://github.com/Nela1901/RouteZero/commit/f291eae) (`test_reporte_pdf.py`) |

Trabajo posterior al compromiso, ya integrado a `main`: historial por día, gráficos y proyección de cierre del mes en el dashboard ([`a9e1faa`](https://github.com/Nela1901/RouteZero/commit/a9e1faa)), pastilla de CO₂ del día y huella digital de la sesión ([`de54ea8`](https://github.com/Nela1901/RouteZero/commit/de54ea8)) y la reducción del impacto ambiental de la Inspección 04. Para la Inspección 05: pruebas de extremo a extremo en tres navegadores con monitoreo de producción, tres workflows de integración y despliegue continuos y la evaluación de usabilidad con la escala SUS.

## Demostración del trabajo completado

**Inspección 05 — viernes 20-11-2026.** Se muestra el sistema desplegado en producción (frontend en Vercel y backend en Render) con datos de demostración cargados en Supabase: un historial de operación del 01-10 al 19-11 y tres rutas en curso para el día de la inspección. Se calienta Render unos minutos antes, porque el plan gratuito tarda entre 30 y 50 s en despertar. Duración máxima: 10 minutos.

Orden de la demostración:

1. **Pantalla Sostenibilidad** (HU-015 y HU-017): indicadores del periodo, resumen de entregas, gráfico de emisiones por día, plan de compensación con árboles y meta mensual. Cambio a un periodo sin jornadas para mostrar los ceros y el aviso.
2. **Reporte PDF** (HU-016): «Descargar reporte PDF» y apertura del archivo; un periodo sin datos muestra el aviso en lugar de un PDF vacío.
3. **Consultas de la base** (HT-11): `python scripts/auditar_consultas.py`, con los 17 tiempos y los índices usados.
4. **Pruebas automatizadas** (HT-12 y Playwright): informe HTML de la suite de extremo a extremo en Chromium, Firefox y WebKit y las mediciones de producción (Web Vitals, tiempos de la API y códigos HTTP), documentadas en [`03 Analisis PlayWrigth`](03%20Analisis%20PlayWrigth%20V_1_0_0.md).
5. **Integración y despliegue continuos**: los tres workflows en GitHub Actions (`ci.yml`, `tests.yml` y `deploy-production.yml`) y su resultado.
6. **Usabilidad**: el puntaje de la escala SUS y lo que los usuarios señalaron, en el informe de usabilidad.

![Pantalla de Sostenibilidad y pastilla de CO₂ en el sistema desplegado](../reduccion%20del%20impacto%20ambiental/evidencias/captura-pastilla-y-sostenibilidad.png)

**Resultados medidos** (detalle en el plan y en la implementación de la sostenibilidad):

| Criterio | Meta | Resultado |
|---|---|---|
| Dashboard en Render (30 días, 450 rutas) | — | 2.4 s; el tiempo es de red hacia la base |
| Plan de compensación en Render (30 días) | — | 2.3 s |
| Reporte PDF en Render | — | 7.5 s el de 30 días y 3.3 s el de un día |
| Consultas críticas de la base (RNF-011, HT-11) | 500 ms o menos | 17 de 17 en 42 ms o menos |
| Cobertura de pruebas del backend | 80 % o más | 98 % (359 pruebas); el módulo `sostenibilidad`, 100 % |
| Pantalla Sostenibilidad en Lighthouse (local) | 90 o más | Accesibilidad, buenas prácticas y SEO en 100; rendimiento 99 en escritorio y 95 en móvil |
| Integración continua | en verde | En los Pull Request del sprint y en las integraciones a `main` |

**Retroalimentación recibida de los usuarios.** La evaluación de usabilidad con la escala SUS y sus comentarios abiertos recoge lo que usuarios con experiencia en los tres roles del sistema (administración, operación y conducción) señalaron al usarlo; los resultados y las mejoras derivadas están en el informe de usabilidad.

**Salvedades:** el precio del combustible (S/ 4.50 por litro), la meta mensual de CO₂ (800 kg) y el CO₂ que absorbe un árbol (22 kg al año) son supuestos sin datos reales de la empresa y se ajustan por variable de entorno; las alianzas de reforestación son propuestas, sin convenios; el combustible ahorrado se mide frente a la solución inicial del optimizador y no frente a una operación real sin optimizar; tras una re-optimización las métricas de una ruta cubren solo el tramo restante.

## Pendientes

- **Datos de la flota real:** cargar el precio de compra y la vida útil de los vehículos y validar los tres supuestos de sostenibilidad con la empresa. Sin ese dato el costo del ciclo de vida de esos vehículos sale como «sin dato».
- **Rendimiento en Render gratuito:** reutilizar las matrices entre peticiones y reducir los viajes a la base (IMP-016 e IMP-019); la primera petición tras un periodo inactivo tarda hasta unos 50 s por el arranque en frío del plan gratuito.
- **Integración continua, fase 2:** las pruebas de integración del backend (359) corren contra la base real de Supabase y se ejecutan en local antes de cada Pull Request; llevarlas a GitHub Actions exigiría una base de pruebas dedicada. En `tests.yml` corren las que no necesitan base de datos.
- **Seguridad:** las brechas de menor prioridad del [plan de OWASP](../Sprint%203/06%20Evaluaci%C3%B3n%20de%20seguridad%20OWASP%20V_1_2_0.md) (cabecera `Content-Security-Policy`, bloqueo de `requirements.txt` con sumas de verificación y MFA obligatorio para el administrador).
- **Heredados:** foto del conductor con Cloudinary, calibración de los factores de hora punta con datos reales, checklist formal de políticas RLS y versión de Python fijada en Render.
- **Aprobación de los Pull Request por un compañero** (criterio 3 del Definition of Done): se cumplió en el [PR #64](https://github.com/Nela1901/RouteZero/pull/64), aprobado en GitHub por Yago Espinoza y Keen Guerra antes del merge; el #62 y el #63 se fusionaron antes, sin aprobación registrada. Es una brecha de proceso (IMP-025).

## Aporte por integrante

La columna «Asignación en Jira» es el dato objetivo del tablero. La columna «Aporte declarado por el equipo» recoge lo que informó la líder del proyecto; no se estima ni se reparte un porcentaje.

| Integrante | Asignación en Jira (Sprint 4) | Aporte declarado por el equipo |
|---|---|---|
| Inciso Aguilar Elizabeth Antonela | Sin ítems propios en el tablero; trabajó junto con Yago en HU-015, HU-016, HU-017 y HT-12 | Construcción de HU-015, HU-016, HU-017, HT-11 y HT-12: el módulo de sostenibilidad, el reporte PDF, el costo del ciclo de vida de la flota, la auditoría y optimización de consultas, las pruebas y las migraciones; mediciones en Render; documentación del sprint |
| Espinoza Tiza Yago Imanol | HU-015, HU-016, HU-017, HT-12 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |
| Uscuvilca Ramos Abraham Luis | Sin ítems propios en el tablero; trabajó junto con Keen en HT-11 | Pruebas del sistema como tester |
| Guerra Lozano Keen | HT-11 | Pruebas del sistema como tester. Aprobó el Pull Request #64 en GitHub |

**Nota de proceso:** los commits y push del repositorio se hacen desde una sola cuenta de GitHub, la de la líder del proyecto, para agilizar la integración. Por eso el historial de Git no refleja por sí solo la autoría de cada integrante y este cuadro es la referencia de quién aportó en qué. Las revisiones se hacen en persona, desde la computadora de la líder, cuando el equipo trabaja junto en clase.

## Metadatos del documento

| Campo | Detalle |
|---|---|
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 4 — Sostenibilidad y Cierre (22-10-2026 – 13-11-2026) |
| **Fecha de la revisión** | Inspección 05, viernes 20-11-2026 |
| **Versión** | 1.0.0 |

---

[← Volver al README principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-17 | Primera versión con la numeración y la plantilla de la consigna de la Inspección 05 (título, líder y tres secciones obligatorias). Continúa el contenido de `03 Revisión del Sprint` V_1_1_0 (versiones anteriores en [`historial Sprint 4`](historial%20Sprint%204/)): se agregan el Pull Request y los commits de cierre y los criterios de aceptación verificados de cada historia, la demostración de la inspección del 20-11-2026 y los pendientes actualizados; el aporte por integrante pasa a una sección final | Inciso Aguilar Elizabeth Antonela |
