# 06 Calidad de la Interfaz y Pruebas de Extremo a Extremo

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Ítems** | HT-09 (Diseño responsive y cumplimiento WCAG 2.1 AA) y HT-10 (Pruebas de integración del mapa interactivo) |
| **Fecha** | 2026-10-22 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../README.md)

---

Este documento registra el trabajo de calidad de la interfaz del Sprint 3: el diseño responsive y la accesibilidad de las pantallas nuevas (HT-09), y las pruebas de extremo a extremo con Playwright y la integración continua (HT-10). Sigue el material del docente *El ecosistema de testing en JavaScript (2026)* y la acción de la retrospectiva del Sprint 2: medir Lighthouse y W3C al terminar cada pantalla.

## 1. Diseño responsive (HT-09)

### 1.1 Hallazgo

Al probar las pantallas de operaciones con el ancho de un celular (412 px) se encontró un problema que no detectaba ninguna prueba de componentes: **el menú lateral aparecía expandido y ocupaba 232 de los 412 px (56 %)**. El contenido quedaba con unos 180 px y la página tenía desplazamiento horizontal (436 px de contenido en una ventana de 412 px). El menú siempre empezaba expandido salvo que el usuario lo hubiera contraído antes.

### 1.2 Correcciones

| Cambio | Efecto |
|---|---|
| El menú lateral empieza **colapsado en pantallas de menos de 900 px** (si el usuario no guardó otra preferencia) | El contenido recupera unos 330 px en el celular. |
| Las listas desplegables de los formularios no pueden ser más anchas que su fila | Desaparece el desborde del panel de incidentes. |
| En el panel del mapa, las filas de cada tramo se parten en dos líneas | El tiempo y la distancia ya no se salen del panel. |
| El panel del mapa tiene un botón **Ocultar panel / Mostrar panel** y en pantallas angostas empieza cerrado | El panel dejaba casi la mitad del mapa tapada en el celular. |

### 1.3 Verificación

- Capturas de las pantallas Mapa y Rutas en tamaño celular antes y después (revisadas a mano).
- Pruebas automáticas en el viewport de un Pixel 7: sin desplazamiento horizontal en el mapa, en Rutas y en la vista del conductor; el panel del mapa queda dentro de la ventana; los botones **Entregado** y **No se pudo** de la vista del conductor miden al menos 44 px de alto (tamaño mínimo de un objetivo táctil).

## 2. Accesibilidad y HTML válido (HT-09)

### 2.1 Método

La auditoría se ejecuta con `npm run auditar` (configuración `playwright.auditoria.config.ts`), aparte de las pruebas normales. Se compila la aplicación y se sirve con los **datos sintéticos** de las pruebas de extremo a extremo; ningún dato real sale del equipo. Se auditan las pantallas del sprint: inicio de sesión, mapa con rutas, rutas, y la vista del conductor con y sin ruta.

- **Lighthouse 13** sobre el navegador de Playwright, en móvil (configuración por defecto: Moto G con red 4G lenta) y en escritorio.
- **Validador Nu del W3C** (el mismo del Sprint 2) sobre el DOM ya renderizado. Una prueba de control con HTML con errores confirmó que el validador los detecta (4 errores y 1 aviso), por lo que el resultado limpio de las pantallas es real.

### 2.2 Resultados al 22-10-2026

| Pantalla | Móvil: rend. / acces. / buenas prácticas / SEO | Escritorio: rend. / acces. / buenas prácticas / SEO | W3C |
|---|---|---|---|
| Inicio de sesión | 95 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 0 errores, 0 avisos |
| Mapa con rutas | 96 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 0 errores, 0 avisos |
| Rutas | 96 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 0 errores, 0 avisos |
| Conductor con ruta | 96 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 0 errores, 0 avisos |
| Conductor sin ruta | 96 / 100 / 100 / 100 | 98 / 100 / 100 / 100 | 0 errores, 0 avisos |

La única observación de Lighthouse es informativa: «Missing source maps for large first-party JavaScript» (la compilación de producción no publica mapas de código).

**Alcance de estos números:** accesibilidad, buenas prácticas y SEO son comparables con producción. El **rendimiento no lo es**: aquí la API simulada responde al instante. Por eso se midió también en producción (sección 2.3).

### 2.3 Lighthouse en producción (22-10-2026)

Se ejecuta con `npm run auditar:produccion` contra Vercel y Render (con `CLAVE_PRUEBA` y una ruta de demostración de hoy, que se borra al terminar): inicia sesión por la API con las cuentas de prueba, inyecta los tokens y mide cada pantalla. Se comprobó que el despliegue tenía la versión del sprint (el panel plegable, el aviso de carga y la corrección responsive estaban en el bundle de Vercel).

| Pantalla | Móvil: rend. / acces. / buenas prácticas / SEO | Escritorio: rend. / acces. / buenas prácticas / SEO | FCP y LCP en móvil | TBT y CLS |
|---|---|---|---|---|
| Mapa | 94 / 100 / 100 / 100 | 91 / 100 / 100 / 100 | 2.4 s y 2.4 s | 0 ms y 0 |
| Rutas | 94 / 100 / 100 / 100 | 98 / 100 / 100 / 100 | 2.5 s y 2.5 s | 0 ms y 0 |
| Conductor | 94 / 100 / 100 / 100 | 98 / 100 / 100 / 100 | 2.5 s y 2.5 s | 0 ms y 0 |

**Todas las mediciones cumplen la meta de 90** (en el Sprint 2 el mapa daba 88-89 y Pedidos 85). El hilo principal no se bloquea (TBT 0 ms) y no hay desplazamientos de diseño; lo que más pesa es el primer dibujo, por la latencia de la API en Render gratuito (IMP-016).

## 3. Pruebas de extremo a extremo (HT-10)

### 3.1 Decisiones

| Decisión | Motivo |
|---|---|
| Playwright, con el Chrome instalado en local y Chromium en CI | Es el estándar de 2026 según el material del docente; multinavegador, emulación de dispositivos móviles y paralelismo gratis. |
| Se prueba la aplicación **compilada** (`vite preview`) | Es lo que se despliega en Vercel. |
| La API se **simula en el navegador** con `page.route`, al mismo origen que la aplicación | Las pruebas no dependen de Render, de Supabase ni de una cuenta con MFA, y no hay problemas de CORS. |
| Los mosaicos de OpenStreetMap se sustituyen por una imagen vacía | Las pruebas no dependen de internet. |
| Cada prueba comprueba que **no haya peticiones sin simular** | Un endpoint nuevo o un cambio de contrato que la interfaz ya use hace fallar la prueba en vez de pasar inadvertido (lección de IMP-017). |
| Selectores por rol y nombre accesible, no por clases CSS | Regla de oro del material: probar lo que ve el usuario. |

### 3.2 Pruebas (19)

| Archivo | Proyecto | Qué comprueba |
|---|---|---|
| `login.spec.ts` (4) | Escritorio | Inicio y cierre de sesión (con su confirmación), credenciales incorrectas, el operador no ve Flota ni Conductores, y la sesión de un conductor entra directo a su vista. |
| `mapa.spec.ts` (5) | Escritorio | Recorridos, paradas numeradas y vías dibujadas, tiempo de cada tramo, ocultar una ruta, cambiar la hora de la congestión, mensaje sin rutas y refresco automático de 30 s (con reloj simulado). |
| `reoptimizacion.spec.ts` (3) | Escritorio | Re-optimizar con hora de referencia, resumen y borrador por confirmar; «sin rutas activas»; el operador no puede re-optimizar. |
| `conductor-movil.spec.ts` (5) | Móvil | Su ruta, registro de una entrega y paso a la siguiente parada, ruta completada, sin ruta, cuenta sin vincular, sin desplazamiento horizontal y botones táctiles. |
| `operaciones-movil.spec.ts` (2) | Móvil | Mapa y Rutas caben en el ancho del celular; el panel del mapa empieza cerrado. |

Comandos (desde `frontend/`): `npm run test:e2e` para las pruebas, `npm run auditar` para Lighthouse y W3C sobre datos sintéticos y `npm run auditar:produccion` para Lighthouse en producción.

## 4. Integración continua, fase 1 (HT-10)

El archivo `.github/workflows/ci.yml` corre en cada Pull Request hacia `main` y en cada integración a `main`, **sin credenciales ni acceso a la base de datos**:

| Trabajo | Qué ejecuta |
|---|---|
| Frontend | `oxlint`, Vitest (con el reporte `github-actions` que anota los fallos en el Pull Request), compilación y `npm audit --audit-level=high`. |
| Pruebas de extremo a extremo | Instala Chromium, corre Playwright y, si algo falla, guarda el informe y las trazas como artefacto durante 7 días. |
| Backend, análisis estático | `bandit -lll` (sin hallazgos de severidad alta) y `pip-audit` de las dependencias. |

Decisiones:

- Se usa `bandit -lll` (solo severidad alta) y no `-ll`: los 16 avisos de severidad media son el mismo falso positivo de SQL (B608, confianza baja) sobre nombres de columna que son constantes del código. El criterio del proyecto es no tener hallazgos de severidad alta.
- `npm audit --audit-level=high`: falla con vulnerabilidades altas o críticas, no con las moderadas, para que un aviso nuevo de una dependencia de desarrollo no bloquee todos los Pull Request.
- **Fase 2 pospuesta:** las pruebas de pytest corren contra la base real de Supabase y no están en CI; se siguen ejecutando en local antes de cada Pull Request. Se reevalúa al terminar todos los sprints (ver [`03 Estrategia y resultados de pruebas`](03%20Estrategia%20y%20resultados%20de%20pruebas%20V_1_6_0.md)).

**Comprobado en GitHub el 22-10-2026:** el Pull Request #59 y la integración a `main` ejecutaron los tres trabajos en verde (frontend 20 s, Playwright 56 s y backend 24 s), con la instalación limpia de Linux. Antes se habían comprobado los comandos uno por uno en local (`npm run lint`, Vitest, la compilación, `npm audit`, las 19 pruebas de Playwright, `bandit -lll` y `pip-audit`).

## 5. Dependencias

Se agregaron como dependencias de desarrollo `@playwright/test` y `lighthouse`. Al instalarlas, `npm audit` avisó de 4 vulnerabilidades (1 alta) que **no venían de las herramientas nuevas** sino de `vite` 8.3.1 y `@vitest/mocker` (herramientas de desarrollo, con 0 al excluirlas). `npm audit fix` falló por un error interno de npm, por lo que se actualizaron a mano `vite` a 8.3.5 y `vitest` y `@vitest/coverage-v8` a 5.0.5: `npm audit` queda en **0 vulnerabilidades** con las 89 pruebas de Vitest y la compilación en verde.

## 6. Limitaciones

- Lighthouse de la sección 2.2 se mide con la API simulada; el de producción (2.3) depende de la latencia de Render y varía entre ejecuciones.
- La validación W3C usa el servicio público del W3C (con el DOM de datos sintéticos): no puede ejecutarse sin internet ni en CI.
- El workflow no ejecuta pytest (fase 2 pospuesta) ni la auditoría de Lighthouse y W3C, que necesitan internet y tardan más.
- Las pruebas de extremo a extremo no ejercitan el backend real: lo cubren las pruebas de pytest.
- Solo se prueban Chrome y Chromium; Firefox y WebKit quedan fuera (orden de recorte del plan).

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-22 | Versión inicial: corrección del diseño responsive, auditoría de Lighthouse y W3C de las pantallas del sprint, pruebas de extremo a extremo con Playwright, integración continua fase 1 y dependencias | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-22 | Se agregan Lighthouse en producción y la comprobación del workflow en GitHub, y se actualizan los comandos y las limitaciones | Inciso Aguilar Elizabeth Antonela |
