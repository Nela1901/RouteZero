# 01 Informe de Reducción del Impacto Ambiental (Green IT)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Actividad** | Inspección 04 — Green Software y verificación de estándares (actividad de cierre del Sprint 4) |
| **Fecha de las mediciones** | 2026-11-09 |
| **Stack evaluado** | React 19 + Vite (Vercel), FastAPI (Render), PostgreSQL (Supabase) |
| **Herramientas** | Lighthouse 13 y Lighthouse CI 0.15.1, Playwright, modelo SWDM v4 verificado contra CO2.js 0.16.9, `svgo`, `curl` |
| **Documento hermano** | [02 Estándares de Ingeniería de Software](02%20Estandares%20Ingenier%C3%ADa%20de%20software%20V_1_0_0.md) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../../../README.md)

---

## 1. Resumen

Se auditó el consumo de datos y de recursos de RouteZero, se aplicaron mejoras en las 8 áreas de optimización de la actividad (adaptadas a nuestro stack, sección 3) y se midió el efecto antes y después con las mismas herramientas y condiciones.

| Indicador (carga inicial de la aplicación) | ANTES | DESPUÉS | Variación |
|---|---|---|---|
| JavaScript inicial (sin comprimir) | 553.4 KB | 281.9 KB | **−49 %** |
| JavaScript inicial (comprimido) | 160.4 KB | 87.4 KB | **−46 %** |
| Peso transferido, móvil | 213 KB | 140 KB | **−34 %** |
| Peso transferido, escritorio | 244 KB | 171 KB | **−30 %** |
| FCP en móvil | 2.18 s | 1.66 s | **−24 %** |
| LCP en escritorio | 797 ms | 488 ms | **−39 %** |
| Peticiones a dominios de terceros | 4 | 0 | **−100 %** |
| Emisión estimada por visita (SWDM v4) | 0.0253 g CO₂e | 0.0169 g CO₂e | **−33 %** |

Estado de las 8 áreas: **5 implementadas o mejoradas en esta actividad o ya cumplidas con evidencia, 1 cubierta por la plataforma, 1 parcial y 1 «no aplica» justificada** (detalle en la sección 5). Lo que **no** se logró está en la sección 9: el FCP y el LCP en móvil siguen por encima de los umbrales de la rúbrica.

Todo es reproducible: los comandos están en la sección 10 y los reportes consolidados en la carpeta [`evidencias/`](../evidencias/).

---

## 2. Sensibilización: impactos ambientales del software

El software contamina de forma indirecta: consume electricidad en cada lugar por el que pasan los datos y exige fabricar hardware. Los impactos se reparten en tres momentos.

| Momento | Impacto ambiental | Ejemplo en RouteZero |
|---|---|---|
| **Desarrollo** | Energía de los equipos de desarrollo y de la integración continua (cada ejecución del pipeline enciende un servidor); dependencias pesadas; pruebas repetidas; fabricación del hardware | El CI corre en cada Pull Request; por eso `green-audit.yml` solo se activa si cambia `frontend/` (sección 8) |
| **Despliegue** | Centros de datos (electricidad y refrigeración), servidores encendidos aunque nadie los use, ubicación geográfica y mezcla eléctrica, hosting no renovable | Vercel y Render no figuran como hosting verde (sección 7.4); Render gratuito se apaga por inactividad (arranque en frío) |
| **Uso** | Red de transmisión, energía del dispositivo del usuario (la parte más grande del consumo por GB), batería del celular, renovación de equipos | El conductor usa un celular: cada KB que no se descarga ahorra energía de red y de batería |

Datos del material del curso (SWDM v4): el consumo operativo por GB transferido es de 0.055 kWh en centros de datos, 0.059 kWh en redes y 0.080 kWh en los dispositivos de los usuarios; las tecnologías de la información representan entre el 1.5 % y el 4 % de las emisiones globales. La intensidad promedio de la electricidad mundial es del orden de 480 a 495 g CO₂e/kWh según la fuente.

Idea central: **menos bytes y menos cómputo = menos energía = menos carbono**. Por eso las optimizaciones de este informe atacan primero la cantidad de datos que viaja y la cantidad de código que el navegador debe ejecutar.

---

## 3. Alcance: las 8 áreas adaptadas a nuestro stack

La actividad enumera 8 áreas pensadas para el stack MERN (MongoDB, Express, React, Node). RouteZero usa otro stack, así que cada área tiene su equivalente directo:

| # | Área de la actividad (MERN) | Equivalente en RouteZero |
|---|---|---|
| 1 | Consultas de MongoDB (`.select()`, `.lean()`, índices) | Consultas SQL de PostgreSQL: columnas necesarias, `JOIN LATERAL`, índices (HT-11) |
| 2 | Paginación | Paginación con `limite` y `desplazamiento` en la API y la tabla de pedidos |
| 3 | Compresión de imágenes (WebP/AVIF) | Formatos de imagen de la aplicación: SVG y mosaicos del mapa |
| 4 | Lazy loading y code splitting | `React.lazy` y `Suspense` con la división de código de Vite |
| 5 | Dependencias innecesarias | Depuración de paquetes de npm y de pip |
| 6 | Reducción de solicitudes HTTP | Menos peticiones y menos dominios externos (fuentes autoalojadas) |
| 7 | Caché de recursos | Cabeceras `Cache-Control` en Vercel y política de caché de la API |
| 8 | Compresión de la API (Brotli/Gzip en Express) | Compresión gzip de las respuestas de la API de FastAPI |

---

## 4. Metodología de medición

| Aspecto | Detalle |
|---|---|
| **Producción** | `npm run auditar:produccion`: Lighthouse sobre Vercel y Render, con las cuentas de prueba y una ruta de demostración de hoy que se borra al terminar. Pantallas: Mapa, Rutas y Conductor |
| **Local** | `npm run auditar`: la aplicación compilada con `vite preview` y la API simulada en el navegador (datos sintéticos). Misma máquina y mismas condiciones antes y después, por eso es la comparación válida del efecto de cada cambio |
| **Perfiles** | **Móvil** (Lighthouse por defecto: celular de gama media con red 4G lenta simulada) y **escritorio** (`desktop-config`) |
| **Métricas** | Rendimiento, FCP, LCP, TBT, CLS, Speed Index, peso transferido y número de peticiones (ver glosario, sección 11) |
| **ANTES** | Código de `main` al 2026-11-09, antes de esta actividad |
| **DESPUÉS** | Código con las mejoras de la sección 5 |
| **Pipeline** | Lighthouse CI con presupuesto de rendimiento (sección 8) |

Límites de la medición, para no sobreinterpretarla:

- El rendimiento **en producción** depende de la latencia de la API en Render gratuito (cada petición cuesta unos 2 s; IMP-016), que no se controla con cambios de código.
- Las mediciones **locales** no incluyen esa latencia; sirven para aislar el efecto de cada cambio.
- Lighthouse es una medición de **laboratorio** (simulada), no de usuarios reales (datos de campo).
- Las cifras del DESPUÉS en producción se actualizarán en la versión siguiente de este informe, una vez desplegado el cambio en Vercel (sección 9).

---

## 5. Las 8 optimizaciones, con código ANTES y DESPUÉS

### 5.1 Consultas e índices de la base de datos (HT-11) — ya cumplida, con evidencia

**Diagnóstico.** Con las tablas casi vacías del desarrollo cualquier consulta parece rápida. Se escribió `backend/scripts/auditar_consultas.py`, que carga en una transacción que siempre se deshace el volumen de seis meses de operación (2 700 rutas, 16 200 pedidos) y mide 17 consultas críticas con `EXPLAIN (ANALYZE)` (el plan real de ejecución de PostgreSQL con sus tiempos).

**Implementación.** Dos mejoras reales:

1. Índice para el listado de pedidos sin filtro de estado, que antes ordenaba todos los pedidos en cada petición.
2. El dashboard y el reporte contaban las paradas de **todas** las rutas del historial aunque se pidiera un solo mes.

ANTES:

```sql
-- Dashboard y reporte: agrupaba las paradas de todo el historial
JOIN (SELECT ruta_id, COUNT(*) AS paradas FROM ruta_pedidos GROUP BY ruta_id) p ON p.ruta_id = r.ruta_id
```

DESPUÉS:

```sql
-- Cuenta solo las paradas de las rutas del periodo (JOIN LATERAL: la subconsulta corre por cada fila de `rutas`)
JOIN LATERAL (SELECT COUNT(*) AS paradas FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) p ON TRUE

-- Índice para ORDER BY creado_en DESC, pedido_id sin filtro de estado
CREATE INDEX IF NOT EXISTS idx_pedidos_creado ON pedidos (creado_en DESC, pedido_id);
```

**Evidencia.** Detalle en [`02 Implementación de la sostenibilidad`](../../../02%20Implementaci%C3%B3n%20de%20la%20sostenibilidad%20V_1_3_0.md), sección 6.

| Consulta | ANTES | DESPUÉS |
|---|---|---|
| Listado de pedidos sin filtro | 7.0 ms | **0.1 ms** |
| Dashboard: totales de 30 días | 6.6 ms | **3.1 ms** |
| Reporte: rutas del periodo | 6.9 ms | **2.5 ms** |
| Las 17 consultas críticas | — | **todas ≤ 42 ms** (umbral: 500 ms) |

Código: [`migracion_indices_ht11.sql`](../../../../../../backend/scripts/migracion_indices_ht11.sql) y [`repository.py` de sostenibilidad](../../../../../../backend/src/sostenibilidad/repository.py).

### 5.2 Paginación — cumplida donde importa; el resto, justificado

**Diagnóstico.** Una lista que devuelve todos sus registros crece sin límite con la operación diaria.

**Implementación.** El listado de **pedidos**, la tabla que más crece (miles de filas), se pagina en el servidor con un máximo de 200 por página:

```python
# backend/src/pedidos/router.py
limite: int = Query(50, ge=1, le=200, description="Pedidos por página (máximo 200)"),
desplazamiento: int = Query(0, ge=0, description="Pedidos que se omiten al inicio"),
```

La auditoría de la API (`limite` de 100 y máximo de 500) también acota el registro de auditoría. **Flota, clientes y conductores no se paginan**: son listas acotadas por el negocio (una flota de unos 15 vehículos, un equipo de conductores), y paginarlas añadiría peticiones y complejidad sin ahorro real. Medición actual: la respuesta completa de clientes pesa 6.9 KB sin comprimir y 1.6 KB comprimida (sección 5.8). Si el número de clientes crece mucho, se paginará con el mismo patrón.

### 5.3 Imágenes — «no aplica», con medición

**Diagnóstico.** La aplicación **no usa imágenes rasterizadas** (PNG o JPEG). Las únicas imágenes son:

| Recurso | Naturaleza | Control |
|---|---|---|
| `favicon.svg` (9.3 KB) | Vectorial | Propio |
| Código QR de MFA en Seguridad | SVG incrustado como imagen (`<img>` con datos), sin petición | Propio |
| Mosaicos del mapa (OpenStreetMap) | PNG de un servicio externo | De terceros |

**Implementación.** Convertir un SVG a WebP o AVIF empeoraría el resultado y perdería la nitidez vectorial. Se minimizó el SVG con `svgo` y se midió:

```text
favicon.svg: 9.299 KiB - 0.2 % = 9.283 KiB
```

Es decir, ya estaba tan reducido como se puede (−0.2 %): no hay ahorro que justifique cambiarlo. Además se eliminó `public/icons.svg` (5 KB), un archivo que ningún componente usaba. Los atributos `width` y `height` y la carga prioritaria de la imagen principal no aplican porque no hay una imagen principal (el CLS medido es de 0.001).

### 5.4 Carga diferida y división de código (`React.lazy`) — implementada

**Diagnóstico.** Todas las pantallas se compilaban en un único archivo de **553 KB** (160 KB comprimido), que incluía Leaflet (la librería de mapas) y las nueve pantallas, y se descargaba entero incluso en el login. Vite lo advertía: *«Some chunks are larger than 500 kB»*.

ANTES (`frontend/src/App.tsx`):

```tsx
import { MapaPage } from "./pages/operaciones/MapaPage";
import { FlotaPage } from "./pages/operaciones/FlotaPage";
// ... las nueve pantallas importadas de forma estática
```

DESPUÉS:

```tsx
// Cada pantalla es su propio trozo de código, que solo se descarga al entrar a ella.
const MapaPage = lazy(() => import("./pages/operaciones/MapaPage").then((m) => ({ default: m.MapaPage })));
const FlotaPage = lazy(() => import("./pages/operaciones/FlotaPage").then((m) => ({ default: m.FlotaPage })));
// ... (las nueve pantallas; el login y el layout siguen cargándose de inmediato)
```

```tsx
// frontend/src/layout/OperacionesLayout.tsx: el menú y el encabezado se quedan mientras baja el trozo
<Suspense fallback={<p role="status" style={{ margin: 0, padding: 24, color: "var(--rz-text-muted)" }}>Cargando…</p>}>
  <Outlet />
</Suspense>
```

**Evidencia.** Salida de `npm run build`:

| Archivo | ANTES | DESPUÉS |
|---|---|---|
| `index.js` (inicial) | 553.40 KB (160.44 comprimido) | **281.92 KB (87.35 comprimido)** |
| `index.css` (inicial) | 17.71 KB | 3.53 KB |
| Leaflet (trozo aparte, solo al abrir una pantalla con mapa) | dentro del inicial | 152.33 KB (44.62 comprimido) + 15.09 KB de CSS |
| Cada pantalla | dentro del inicial | de 6.6 KB (Clientes) a 17.3 KB (Rutas) |

Efecto medido en el login (local): peso 213 → 140 KB en móvil y FCP móvil 2.18 → 1.66 s. Una observación honesta: en el Mapa, que es la pantalla que más trozos encadena (Leaflet incluido), el LCP móvil subió de 2.17 s a 2.45 s en una de las corridas con solo esta mejora y volvió a 1.8 s en las siguientes; es variación entre ejecuciones, no una mejora ni un empeoramiento confirmado.

**Validación de que no se rompió nada:** 147 de 147 pruebas de Vitest y 33 de 33 de Playwright (escritorio y celular), antes y después.

### 5.5 Dependencias — ya mínimas

**Diagnóstico.** Se revisaron las dependencias de ejecución del frontend:

```json
"dependencies": {
  "leaflet": "^1.9.4", "react": "^19.2.8", "react-dom": "^19.3.1",
  "react-leaflet": "^5.0.0", "react-router-dom": "^7.18.4"
}
```

Son **5 paquetes**, todos imprescindibles (interfaz, rutas y mapa). No hay librerías de fechas (`moment`) ni de utilidades (`lodash`) que reemplazar por las funciones nativas del navegador. En el backend, `numpy` y `scipy` sostienen el motor de optimización (ACO) y `fpdf2` genera el reporte PDF: cada una tiene un uso concreto.

**Implementación.** Lo único sobrante era el archivo `public/icons.svg` (sección 5.3), ya eliminado. Para que no vuelva a acumularse: Dependabot propone actualizaciones, y el CI ejecuta `npm audit --audit-level=high`, Bandit y `pip-audit` en cada Pull Request. El peso del paquete más grande (Leaflet, 44.6 KB comprimidos) se aísla con la carga diferida de la sección 5.4, de modo que solo lo paga quien abre un mapa.

### 5.6 Solicitudes HTTP y recursos de terceros — implementada

**Diagnóstico.** Al medir las peticiones del login en producción se encontraron **4 peticiones a dominios de terceros** (Google Fonts): una hoja de estilos externa que bloquea el primer dibujo y tres archivos de fuentes (24.5 + 31.4 + 22.3 = **78 KB**, cerca de un tercio del peso total de 218 KB).

```text
200 | text/css   | fonts.googleapis.com/css2?family=Space+Grotesk...   <- bloquea el primer dibujo
200 | font/woff2 | fonts.gstatic.com/.../manrope/...woff2             24.5 KB
200 | font/woff2 | fonts.gstatic.com/.../jetbrainsmono/...woff2       31.4 KB
200 | font/woff2 | fonts.gstatic.com/.../spacegrotesk/...woff2        22.3 KB
```

ANTES (`frontend/index.html`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet" />
```

DESPUÉS: se quitan esas tres líneas y las **mismas tres familias** (licencia SIL Open Font License 1.1) se sirven desde nuestro propio dominio, en su versión variable y solo con el subconjunto latino que cubre el español:

```css
/* frontend/src/theme/tokens.css (una de las tres) */
@font-face {
  font-family: "Manrope";
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url("../assets/fonts/manrope-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, /* ... subconjunto latino ... */;
}
```

Se probó también la alternativa de seguir con Google Fonts pidiendo pesos variables (`wght@400..700`): **no cambió nada medible**, porque Google ya servía un archivo por familia. Lo que sí ayudó fue autoalojar.

**Evidencia** (verificado en el navegador con la aplicación compilada):

```text
Fuentes: Space Grotesk 500 700 loaded | Manrope 400 700 loaded | JetBrains Mono 500 600 loaded
Peticiones a dominios externos: 0
font-family del body: Manrope, sans-serif
```

Efecto medido en escritorio (local): FCP 510 → 368 ms (−28 %) y LCP 797 → 488 ms (−39 %). En móvil no hubo mejora adicional (el FCP móvil se mantiene en 1.66 s, limitado por la simulación de red lenta). El aspecto visual no cambia: las mismas familias y los mismos pesos.

### 5.7 Caché de recursos — implementada (verificación en producción pendiente del despliegue)

**Diagnóstico.** Se inspeccionaron las cabeceras reales de Vercel. Los archivos de `/assets/` llevan un **nombre con hash** (`index-DE2H_Ds6.js`): si el contenido cambia, cambia el nombre. Aun así se servían con:

```text
Cache-Control: public, max-age=0, must-revalidate
Etag: "4744734762dc3ca4a2cf71a3e626d64a"
```

Es decir, el navegador volvía a preguntar al servidor si el archivo había cambiado en **cada visita** (una petición de validación que responde 304), aunque ese nombre nunca puede cambiar de contenido.

ANTES: sin regla para `/assets/`. DESPUÉS (`frontend/vercel.json`):

```json
{
  "source": "/assets/(.*)",
  "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
}
```

`max-age=31536000` es un año en segundos e `immutable` le dice al navegador que no valide el archivo mientras no caduque. El `index.html` **no** se cachea así: debe revalidarse para que apunte a los archivos nuevos tras cada despliegue.

**Decisión sobre la API.** Las respuestas de la API llevan `Cache-Control: no-store` **a propósito** (OWASP A02: que el navegador o un intermediario no guarde datos autenticados, ver [`backend/src/main.py`](../../../../../../backend/src/main.py)). Con `no-store` no tiene sentido emitir ETag ni usar una caché de datos en el cliente (como TanStack Query, que la rúbrica de MERN menciona): se contradiría la política de seguridad. La caché útil de datos está en el servidor: el mapa con los trazados por calles tarda 9.3 s la primera vez y 2.6 s desde la caché.

**Verificación pendiente.** La cabecera nueva solo se puede comprobar en producción cuando se fusione y Vercel despliegue: `curl -sI https://route-zero-omega.vercel.app/assets/<archivo>.js` debe mostrar `immutable`. Se anotará en la versión siguiente de este informe.

### 5.8 Compresión de la API — cubierta por la plataforma, con medición

**Diagnóstico.** No hay un `GZipMiddleware` en FastAPI. Se midieron tres respuestas reales de la API en Render, con y sin permitir la compresión:

| Endpoint | Sin comprimir | Comprimido con gzip | Reducción |
|---|---|---|---|
| `GET /api/pedidos` | 18 283 B | 3 073 B | **83 %** |
| `GET /api/clientes` | 6 878 B | 1 599 B | **77 %** |
| `GET /api/rutas/mapa` | 5 791 B | 1 651 B | **72 %** |

La respuesta llega con `Content-Encoding: gzip`: **el proxy de Render ya comprime**. El frontend (Vercel) además entrega los archivos estáticos con Brotli.

**Decisión.** No se añadió compresión en la aplicación. Hacerlo duplicaría el trabajo con 0.1 CPU en el plan gratuito, y comprimiría también el reporte PDF, que ya es un formato comprimido (se medían 7.5 s para el PDF de 30 días). Se documenta la medición como evidencia y el supuesto: si en el futuro se despliega fuera de Render, se agregará `GZipMiddleware(minimum_size=1024)` de Starlette, excluyendo el PDF.

---

## 6. Resultados antes y después

### 6.1 Comparación controlada (local, mismas condiciones), pantalla de inicio de sesión

| Métrica | Móvil ANTES | Móvil DESPUÉS | Escritorio ANTES | Escritorio DESPUÉS |
|---|---|---|---|---|
| Rendimiento (0 a 100) | 96 | **99** | 100 | 100 |
| FCP | 2 176 ms | **1 657 ms** | 510 ms | **368 ms** |
| LCP | 2 176 ms | **1 807 ms** | 797 ms | **488 ms** |
| TBT | 7 ms | 0 ms | 0 ms | 0 ms |
| CLS | 0.004 | 0.006 | 0.001 | 0.001 |
| Speed Index | 2 176 ms | 1 657 ms | 510 ms | 368 ms |
| Peso transferido | 213 KB | **140 KB** | 244 KB | **171 KB** |
| Peticiones | 7 | 7 | 8 | 8 |

Después de los cambios, accesibilidad, buenas prácticas y SEO quedan en **100** en las doce mediciones (seis pantallas × dos perfiles) y el rendimiento mínimo es 99; antes, el mínimo de rendimiento era 95 y una medición (Mapa en móvil) tenía 96 en buenas prácticas. Reporte completo: [`lighthouse-local-ANTES-2026-11-09.json`](../evidencias/lighthouse-local-ANTES-2026-11-09.json) y [`lighthouse-local-DESPUES-2026-11-09.json`](../evidencias/lighthouse-local-DESPUES-2026-11-09.json).

### 6.2 Producción ANTES (2026-11-09, Vercel y Render)

| Pantalla | Perfil | Rend. | FCP | LCP | TBT | CLS | Peso | Peticiones |
|---|---|---|---|---|---|---|---|---|
| Mapa | Escritorio | 98 | 713 ms | 1 004 ms | 0 ms | 0.001 | 248 KB | 8 |
| Rutas | Escritorio | 99 | 696 ms | 696 ms | 0 ms | 0.001 | 248 KB | 8 |
| Conductor | Escritorio | 100 | 682 ms | 682 ms | 0 ms | 0.001 | 248 KB | 8 |
| Mapa | Móvil | 96 | 2 296 ms | 2 296 ms | 6 ms | 0 | 218 KB | 7 |
| Rutas | Móvil | 96 | 2 237 ms | 2 256 ms | 0 ms | 0 | 218 KB | 7 |
| Conductor | Móvil | 96 | 2 304 ms | 2 304 ms | 0 ms | 0 | 218 KB | 7 |

Reporte: [`lighthouse-produccion-ANTES-2026-11-09.json`](../evidencias/lighthouse-produccion-ANTES-2026-11-09.json). Dato operativo del día: Render tardó **52 s** en responder tras su arranque en frío y el proyecto de Supabase estaba pausado por inactividad (plan gratuito); hubo que restaurarlo antes de medir.

### 6.3 Cumplimiento de los umbrales de la rúbrica

| Umbral | Escritorio (producción ANTES) | Escritorio (local DESPUÉS) | Móvil (local DESPUÉS) |
|---|---|---|---|
| Rendimiento ≥ 90 | 98 a 100 ✔ | 100 ✔ | 99 ✔ |
| FCP ≤ 1.0 s | 0.68 a 0.71 s ✔ | 0.37 s ✔ | **1.66 s ✘** |
| LCP ≤ 1.4 s | 0.68 a 1.00 s ✔ | 0.49 s ✔ | **1.81 s ✘** |
| TBT ≤ 85 ms | 0 ms ✔ | 0 ms ✔ | 0 ms ✔ |
| CLS ≤ 0.02 | 0.001 ✔ | 0.001 ✔ | 0.006 ✔ |
| Peso ≤ 1.1 MB | 248 KB ✔ | 171 KB ✔ | 140 KB ✔ |

**En escritorio se cumplen todos los umbrales; en móvil, el FCP y el LCP no.** La causa es la simulación de móvil de Lighthouse (red 4G lenta y CPU reducida), más la latencia de Render en producción; con el código actual el piso medido es de 1.6 s. Se declara así, sin forzar las cifras.

### 6.4 Evolución histórica

El proyecto ya había mejorado antes de esta actividad. Lighthouse en producción: en el Sprint 2 el mapa daba 88 a 89 y Pedidos 85 de rendimiento; el 22-10-2026 todas las pantallas quedaron entre 91 y 98 (detalle en [`06 Calidad de la interfaz y pruebas de extremo a extremo`](../../../../Sprint%203/06%20Calidad%20de%20la%20interfaz%20y%20pruebas%20de%20extremo%20a%20extremo%20V_1_1_0.md), sección 2.3).

---

## 7. Huella de carbono con el modelo SWDM v4

### 7.1 El modelo

**SWDM** (*Sustainable Web Design Model*, Modelo de Diseño Web Sostenible) estima la energía y las emisiones de transferir datos por internet. Lo desarrolla la Green Web Foundation y es la base de CO2.js. Divide cada GB transferido en **tres segmentos** (centro de datos, red y dispositivo del usuario) y en **dos componentes**:

| Segmento | Energía operativa (kWh/GB) | Energía incorporada (kWh/GB) |
|---|---|---|
| Centro de datos | 0.055 | 0.012 |
| Red de transmisión | 0.059 | 0.013 |
| Dispositivo del usuario | 0.080 | 0.081 |
| **Total** | **0.194** | **0.106** |

- **Energía operativa:** la electricidad que se gasta al usar el equipo.
- **Energía incorporada** (*embodied*): la energía que costó fabricar el hardware, repartida por uso. El material del curso solo muestra la operativa; el modelo completo suma ambas (**0.300 kWh/GB**).

Fórmulas:

```text
energía (kWh)   = GB transferidos × kWh/GB de cada segmento y componente
emisión (g CO2e) = energía (kWh) × intensidad de la red eléctrica (g CO2e/kWh)
```

Parámetros usados:

| Parámetro | Valor | Fuente |
|---|---|---|
| Intensidad global | 494 g CO₂e/kWh | Constante de SWDM v4 en CO2.js 0.16.9 (las diapositivas del curso citan 481; se muestra la sensibilidad) |
| Intensidad de Perú | 263.27 g CO₂e/kWh | Datos de promedio de CO2.js |
| Hosting verde | No (factor 0) | Green Web Foundation: Vercel y Render no figuran como verdes (consulta del 2026-11-10) |
| Visitas | 75 % nuevas y 25 % de retorno, que recargan el 2 % de los datos | Valores por defecto del modelo |
| 1 GB | 1 000 000 000 bytes | Igual que CO2.js |

La intensidad del país afecta solo a la energía **operativa**; la incorporada usa siempre la global, como en la implementación de referencia.

### 7.2 Ejemplo calculado paso a paso

Carga inicial en **móvil ANTES**: 213 KB = 213 × 1 024 = 218 112 bytes = 0.000218112 GB.

| Segmento | Energía operativa (kWh) | Emisión operativa (g) | Energía incorporada (kWh) | Emisión incorporada (g) |
|---|---|---|---|---|
| Centro de datos | 0.000218112 × 0.055 = 1.1996 × 10⁻⁵ | × 494 = 0.005926 | × 0.012 = 2.617 × 10⁻⁶ | × 494 = 0.001293 |
| Red | × 0.059 = 1.2869 × 10⁻⁵ | × 494 = 0.006357 | × 0.013 = 2.835 × 10⁻⁶ | × 494 = 0.001401 |
| Dispositivo | × 0.080 = 1.7449 × 10⁻⁵ | × 494 = 0.008620 | × 0.081 = 1.7667 × 10⁻⁵ | × 494 = 0.008728 |
| **Suma** | **4.2314 × 10⁻⁵ kWh** | **0.020903 g** | **2.3120 × 10⁻⁵ kWh** | **0.011421 g** |

**Energía total = 6.543 × 10⁻⁵ kWh; emisión total = 0.020903 + 0.011421 = 0.032324 g CO₂e.**

### 7.3 Resultados

Carga inicial (visita nueva, intensidad global):

| Perfil | Momento | Peso (KB) | Energía total (kWh) | Emisión (g CO₂e) |
|---|---|---|---|---|
| Móvil | ANTES | 213 | 6.543 × 10⁻⁵ | 0.032324 |
| Móvil | DESPUÉS | 140 | 4.301 × 10⁻⁵ | 0.021246 |
| Escritorio | ANTES | 244 | 7.496 × 10⁻⁵ | 0.037029 |
| Escritorio | DESPUÉS | 171 | 5.253 × 10⁻⁵ | 0.025950 |

**Proyección anual.** Escenario declarado como **supuesto** (no son datos de operación real): 20 usuarios (1 administrador, 4 operadores y 15 conductores, uno por vehículo) × 260 días hábiles × 2 sesiones = **10 400 visitas/año**, con 75 % desde celular (los conductores).

| Concepto | ANTES | DESPUÉS | Ahorro |
|---|---|---|---|
| Peso ponderado por visita | 220.75 KB | 147.75 KB | 33.1 % |
| Emisión por visita | 0.025293 g | 0.016929 g | 33.1 % |
| Energía al año | 0.5325 kWh | 0.3564 kWh | 0.1761 kWh |
| **Emisión al año** | **263.04 g CO₂e** | **176.06 g CO₂e** | **86.99 g CO₂e** |

Sensibilidad del ahorro anual (g CO₂e): con la intensidad de las diapositivas (481) son 85.51 g; con la intensidad de Perú en el dispositivo (263.27), 76.15 g; y si el sistema tuviera 500 000 visitas al año (la escala del ejemplo del curso), el ahorro sería de 4 182 g (4.2 kg) con la intensidad global. Tabla completa: [`calculo-swdm-v4.md`](../evidencias/calculo-swdm-v4.md).

### 7.4 Verificación y límites

- **Verificación cruzada:** el script [`scripts/calcular_huella_swdm.py`](../../../../../../scripts/calcular_huella_swdm.py) con `--verificar` coincide con CO2.js 0.16.9 (`perByte` y `perVisitTrace`) a seis decimales en ocho casos, incluido el escenario de Perú. Resultado: [`verificacion-swdm-v4-contra-co2js.txt`](../evidencias/verificacion-swdm-v4-contra-co2js.txt).
- **Solo cuenta la carga de la página.** No incluye las respuestas de la API durante la sesión (unos pocos KB comprimidos por petición) ni el cómputo del motor de optimización.
- **Magnitud:** los gramos son pequeños porque la aplicación es liviana y de uso interno. Lo relevante es el cambio relativo (−33 %) y el contraste con el propósito del sistema: el tope mensual de emisiones de la flota que vigila el módulo de sostenibilidad (RN-010) está configurado en 800 kg de CO₂, mientras que la huella digital anual de la plataforma es de unos 0.18 kg. El mayor efecto ambiental del sistema está en las rutas que optimiza, no en las páginas que sirve.
- **Hosting:** Vercel y Render no están en el directorio de hosting verde. Elegir un proveedor verificado reduciría la parte del centro de datos; hoy no hay descuento.

---

## 8. Automatización: Lighthouse CI y presupuesto de rendimiento

**Idea.** Una optimización se pierde con el tiempo si nada la vigila: una dependencia nueva puede arruinar el rendimiento sin que nadie lo note. **Lighthouse CI (LHCI)** ejecuta Lighthouse automáticamente en cada Pull Request y **falla** si se supera un **presupuesto de rendimiento** (límites que el código no puede sobrepasar).

| Archivo | Función |
|---|---|
| [`.github/workflows/green-audit.yml`](../../../../../../.github/workflows/green-audit.yml) | Workflow de GitHub Actions: compila, mide el peso, ejecuta LHCI en escritorio (falla) y móvil (FCP y LCP solo avisan), resume las métricas y guarda los informes como artefacto (no los publica en ningún servicio externo) |
| [`frontend/lighthouserc.json`](../../../../../../frontend/lighthouserc.json) | Presupuesto de escritorio: rendimiento, accesibilidad, buenas prácticas y SEO ≥ 90; FCP ≤ 1.0 s; LCP ≤ 1.4 s; TBT ≤ 85 ms; CLS ≤ 0.02; peso ≤ 1.1 MB |
| [`frontend/lighthouserc.movil.json`](../../../../../../frontend/lighthouserc.movil.json) | Presupuesto de móvil (más holgado) |

Decisiones:

- **Se activa solo si cambia `frontend/`** (o el propio workflow) y de forma manual: no gasta minutos ni energía en cambios que no pueden afectar el rendimiento.
- **Mide la pantalla pública (el login).** El resto exige sesión; esas pantallas se siguen midiendo con `npm run auditar:produccion`.
- **Acciones fijadas por hash de commit**, igual que nuestro `ci.yml`, y `@lhci/cli@0.15.1` con versión exacta.

Verificación local de que **funciona de verdad**: con el presupuesto actual pasa las 3 repeticiones (rendimiento 100, FCP 0.37 s, LCP 0.49 s, TBT 0 ms, peso 171 KB); y con una copia que exigía FCP ≤ 100 ms **falló con código de salida 1** (`expected: <=100, found: 371`). La primera ejecución en GitHub Actions queda como evidencia en la pestaña *Actions* del Pull Request.

---

## 9. Limitaciones y trabajo futuro

| Limitación | Detalle |
|---|---|
| FCP y LCP en móvil | 1.66 s y 1.81 s contra 1.0 s y 1.4 s de la rúbrica. Se podría reducir aún más separando `react-router` y `react-dom` en trozos con su propia caché, o pasando a renderizado en servidor, a costa de mucha más complejidad |
| Cifras de producción DESPUÉS | Requieren el despliegue en Vercel; se agregarán en la versión 1.1.0 junto con la verificación de la cabecera `immutable` |
| Latencia de Render gratuito | Arranque en frío de 52 s y unos 2 s por petición (IMP-016): no depende del código |
| Pausa de Supabase | El plan gratuito pausa el proyecto tras días sin uso; ocurrió el 2026-11-09 y hubo que restaurarlo |
| Hosting no verde | Vercel y Render no figuran como verdes; cambiar de proveedor excede el alcance |
| Paginación de flota, clientes y conductores | Justificada en la sección 5.2; se hará si el volumen crece |
| Brotli y TanStack Query | No se usan: la compresión la hace la plataforma y la caché de datos choca con `no-store` (secciones 5.7 y 5.8) |
| Alcance del cálculo SWDM | Solo transferencia de la página; no incluye API ni cómputo del motor |

---

## 10. Reproducción y gestión de versiones

Desde `frontend/`:

```powershell
npm run build                       # tamaños de los trozos de código
npm run auditar                     # Lighthouse y W3C locales (datos sintéticos)
npx --yes @lhci/cli@0.15.1 autorun --config=lighthouserc.json   # presupuesto de escritorio
$env:CLAVE_PRUEBA="..."; npm run auditar:produccion              # producción (necesita la ruta de demostración)
```

Desde la raíz del repositorio:

```powershell
python scripts/calcular_huella_swdm.py              # tablas del cálculo SWDM v4
python scripts/calcular_huella_swdm.py --verificar  # contraste con CO2.js
python scripts/verificar_enlaces.py                 # enlaces de los .md
```

Secuencia de Git de esta entrega (rama `sprint4`, Pull Request a `main`):

```powershell
git status
mkdir "docs/03 Ejecución/Sprint 4/Implementación/reduccion del impacto ambiental"   # estructura de la carpeta
git add "docs/03 Ejecución/Sprint 4/Implementación/reduccion del impacto ambiental/"
git commit -m "docs(sprint4): informe de reduccion del impacto ambiental y estandares de ingenieria de software"
git push origin sprint4
```

---

## 11. Glosario

| Término | Explicación breve |
|---|---|
| **Green IT / Green Software** | Diseñar y operar software gastando la menor energía y carbono posible |
| **SWDM v4** | *Sustainable Web Design Model*, versión 4: modelo que convierte bytes transferidos en energía y gramos de CO₂e |
| **kWh** | Kilovatio-hora: unidad de energía (1 kW funcionando durante 1 hora) |
| **g CO₂e** | Gramos de dióxido de carbono equivalente: unidad común para todos los gases de efecto invernadero |
| **Intensidad de la red eléctrica** | Gramos de CO₂e emitidos por cada kWh de electricidad; cambia según el país y su mezcla de fuentes |
| **Energía operativa / incorporada** | La que se gasta al usar un equipo / la que costó fabricarlo |
| **Hosting verde** | Alojamiento cuya energía viene verificada de fuentes renovables |
| **Lighthouse** | Herramienta de Google que audita una página: rendimiento, accesibilidad, buenas prácticas y SEO |
| **Lighthouse CI (LHCI)** | Ejecuta Lighthouse automáticamente en el pipeline y compara contra un presupuesto |
| **Presupuesto de rendimiento** | Límites numéricos (tiempo, peso) que el proyecto se obliga a no superar |
| **FCP** | *First Contentful Paint*: tiempo hasta dibujar el primer contenido |
| **LCP** | *Largest Contentful Paint*: tiempo hasta dibujar el elemento más grande de la pantalla |
| **TBT** | *Total Blocking Time*: tiempo que el hilo principal del navegador queda bloqueado ejecutando JavaScript |
| **CLS** | *Cumulative Layout Shift*: cuánto «saltan» los elementos mientras carga la página |
| **Speed Index** | Qué tan rápido se va llenando visualmente la pantalla |
| **Perfil móvil / escritorio** | Condiciones simuladas de Lighthouse: celular de gama media con 4G lenta, o computadora con red rápida |
| **Datos de laboratorio / de campo** | Medición simulada y repetible / medición de usuarios reales |
| **Arranque en frío** | Demora de un servidor gratuito que se apagó por inactividad y debe volver a encenderse |
| **Bundle / trozo (chunk)** | Archivo de JavaScript que genera la compilación; dividirlo permite cargar solo lo necesario |
| **Code splitting / lazy loading** | Dividir el código y descargar cada parte cuando se necesita (carga diferida) |
| **`React.lazy` y `Suspense`** | Herramientas de React para cargar un componente a demanda y mostrar un mensaje mientras llega |
| **Cache-Control / ETag / `immutable`** | Cabeceras que dicen al navegador cuánto tiempo guardar un archivo, cómo validarlo y que nunca cambiará |
| **gzip / Brotli** | Algoritmos que comprimen las respuestas para que viajen menos bytes |
| **Índice (SQL)** | Estructura que permite a la base de datos encontrar filas sin recorrer toda la tabla |
| **`EXPLAIN (ANALYZE)`** | Instrucción de PostgreSQL que ejecuta una consulta y muestra su plan real y tiempos |
| **`JOIN LATERAL`** | Unión donde la subconsulta puede usar valores de la fila actual, útil para contar solo lo necesario |
| **Paginación** | Devolver los registros en páginas en vez de todos a la vez |
| **Fuente variable / `woff2`** | Archivo de tipografía que contiene todos los pesos / formato web comprimido de fuentes |
| **`unicode-range`** | Qué caracteres cubre un archivo de fuente; el navegador solo lo descarga si hacen falta |
| **`font-display: swap`** | Muestra el texto de inmediato con una fuente del sistema y cambia cuando llega la propia |
| **Terceros (*third parties*)** | Recursos servidos por otros dominios; cada uno suma peticiones y dependencias externas |

---

[← Volver al README Principal](../../../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-09 | Versión inicial: diagnóstico, 8 optimizaciones con código antes y después, mediciones de Lighthouse en producción y local, cálculo de la huella de carbono con SWDM v4 y Lighthouse CI | Inciso Aguilar Elizabeth Antonela |
