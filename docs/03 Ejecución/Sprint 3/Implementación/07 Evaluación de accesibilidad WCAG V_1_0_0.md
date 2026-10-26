# 07 Evaluación de Accesibilidad Web (WCAG)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (Inspección 03) |
| **Fecha de la evaluación** | 2026-10-26 |
| **Nivel de conformidad objetivo** | WCAG 2.2 Nivel AA (el proyecto partió de WCAG 2.1 AA; ver `13. Restricciones`) |
| **Herramientas utilizadas** | Lighthouse 13, validador W3C (Nu), Playwright, revisión del código y de SonarQube Cloud |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../README.md)

---

## 1. Resumen de Accesibilidad por Principios

Se evaluaron los criterios de WCAG 2.2 niveles A y AA que aplican al sistema (tabla de la sección 3). El porcentaje de cada principio es **sobre los criterios evaluados** y no sobre la norma completa: hay criterios sin verificar y no se hizo una prueba con lectores de pantalla.

- **Perceptible:** 11 de 12 criterios evaluados cumplen (92 %); 0 parcial(es) y 1 sin verificar; 1 no aplican.
- **Operable:** 14 de 16 criterios evaluados cumplen (88 %); 2 parcial(es) y 0 sin verificar; 1 no aplican.
- **Comprensible:** 9 de 10 criterios evaluados cumplen (90 %); 1 parcial(es) y 0 sin verificar; 1 no aplican.
- **Robusto:** 2 de 2 criterios evaluados cumplen (100 %); 0 parcial(es) y 0 sin verificar; 0 no aplican.
- **Total:** 36 de 40 criterios evaluados cumplen (90 %), 3 parcial(es) y 1 sin verificar; 3 no aplican.

### Mediciones automáticas

| Medición | Resultado |
|---|---|
| Lighthouse, accesibilidad, 6 pantallas × móvil y escritorio × tema oscuro y claro | **100 en las 24 mediciones** |
| Validador W3C del HTML renderizado | **0 errores y 0 avisos** en las 6 pantallas |
| Pruebas de accesibilidad | 7 de Playwright (campos de acceso, títulos, saltar al contenido, foco visible, reflujo a 320 y 640 px, espaciado de texto) y 1 de Vitest (errores como alerta) |
| Pruebas en total | 33 de extremo a extremo (escritorio y celular) y 100 de Vitest |
| Reglas de accesibilidad de SonarQube (reliability, etiquetas, teclado) | 37 incidencias de fiabilidad en el primer análisis; las de accesibilidad se corrigieron (ver sección 2) |

**Qué no mide Lighthouse y por eso se revisó aparte:** foco visible, saltar bloques, títulos por pantalla, finalidad de los campos, reflujo, espaciado del texto y operación con teclado. Son los hallazgos de la sección 2.

## 2. Hallazgos Principales y Correcciones

| Criterio de Conformidad | Problema Detectado | Componente Afectado | Solución Aplicada |
|---|---|---|---|
| **1.1.1 Contenido no textual** | 15 íconos SVG sin nombre accesible (SonarQube) | Menú lateral, botón de tema, inicio de sesión | Los íconos son decorativos: se marcaron con `aria-hidden="true"` |
| **1.3.5 y 3.3.8 Finalidad del campo y autenticación accesible** | Los campos de correo, contraseña y código no declaraban `autoComplete`, lo que impide el autocompletado y dificulta a quien no puede transcribir códigos | Inicio de sesión | Se agregó `username`, `current-password` y `one-time-code`; prueba de Playwright |
| **2.4.1 Evitar bloques** | Para llegar al contenido había que recorrer todo el menú con el teclado | Estructura de las pantallas de operaciones | Enlace «Saltar al contenido» visible solo al enfocarlo, que lleva el foco al área principal; prueba de Playwright |
| **2.4.2 Página titulada** | Todas las pantallas se llamaban «RouteZero», por lo que un lector de pantalla no anunciaba el cambio de sección | Todas las pantallas | Cada sección fija su título («Rutas · RouteZero»); prueba de Playwright |
| **2.4.6 Encabezados** | La pantalla del mapa no tenía ningún título `h1` | Mapa con rutas | Título `h1` «Mapa de rutas» solo para lectores de pantalla (`rz-solo-lectores`) |
| **2.4.7 Foco visible** | El contorno del foco dependía del navegador | Todos los controles | Regla `:focus-visible` con contorno de 2 px; prueba de Playwright |
| **2.1.1 Teclado y 4.1.2 Nombre, función, valor** | Los diálogos tenían manejadores de clic en el contenedor de la ventana, lo que SonarQube marca como elemento no interactivo | Ventanas modales y diálogo de confirmación | El clic en el fondo cierra la ventana y el contenedor ya no escucha clics; se mantiene Escape |
| **2.4.3 Orden del foco** | Dos campos usaban `autoFocus`, que mueve el foco al cargar la página | Inicio de sesión y activación del MFA | Se enfocan por código cuando el campo aparece tras una acción de la persona |
| **4.1.3 Mensajes de estado y 3.3.1 Identificación de errores** | 17 mensajes de error en línea (formularios de flota, clientes, conductores, pedidos, rutas, seguridad e incidentes) no tenían ningún rol, así que un lector de pantalla no los anunciaba; los avisos de estado eran `div` con `role="status"` | Formularios y avisos de todas las pantallas | Los errores llevan `role="alert"`; los avisos usan el elemento nativo `<output>` donde el contenido lo permite y, en las tarjetas con bloques, se mantuvo `role="status"` porque `<output>` solo admite contenido en línea (el validador W3C lo detectó); prueba de Vitest |
| **1.3.1 Información y relaciones** | Contenedores `div` con `role="main"` y `role="region"` | Estructura de las pantallas | Se reemplazaron por `<main>` y `<section aria-label>` |
| **1.4.10 Reflujo (WCAG 1.4.4)** | En el celular el menú ocupaba el 56 % del ancho y el contenido se desbordaba (Sprint 3, HT-09) | Menú lateral y pantallas de operaciones | El menú empieza colapsado bajo 900 px y el panel del mapa es plegable; pruebas a 320 y 640 px |
| **1.4.1 Uso del color** | El estado de una entrega y el nivel de congestión se distinguían por color | Mapa y vista del conductor | Cada estado tiene símbolo y texto (✓, ✗, «Entregado», «Congestión moderada») |

### Criterios no cumplidos del todo y sin verificar

| Criterio | Situación | Qué haría falta |
|---|---|---|
| 2.1.1 Teclado (parcial) | Los marcadores del mapa de Leaflet no reciben el foco del teclado | Hacer enfocables los marcadores o ofrecer una lista navegable de paradas junto al mapa; hoy la misma información está en el panel |
| 2.2.1 Tiempo ajustable (parcial) | Los avisos emergentes desaparecen a los 3.5 s | Permitir cerrarlos o mantenerlos mientras tienen el foco |
| 3.3.3 Sugerencia ante errores (parcial) | Los errores de validación genéricos solo nombran el campo | Mensajes específicos por campo (rango válido, formato esperado) |
| 1.4.11 Contraste de componentes no textuales | No se midió el contraste de bordes de campos ni de las marcas del mapa | Revisión con una herramienta de contraste |
| Lectores de pantalla | No se probó con NVDA ni VoiceOver | Prueba manual con un lector de pantalla en las pantallas principales |

## 3. Detalle por criterio

| Criterio | Nivel | Resultado | Método y evidencia |
|---|---|---|---|
| 1.1.1 Contenido no textual | A | Cumple | Lighthouse y revisión: los íconos decorativos llevan `aria-hidden`, el código QR tiene texto alternativo y el gráfico de emisiones muestra además el valor en texto |
| 1.2.x Medios con el tiempo | A/AA | No aplica | El sistema no tiene audio ni video |
| 1.3.1 Información y relaciones | A | Cumple | Lighthouse y W3C (0 errores): puntos de referencia `nav`, `main` y `header`, `label` asociado a cada campo y jerarquía de títulos |
| 1.3.2 Secuencia significativa | A | Cumple | Revisión: el orden del DOM coincide con el visual, y la tabulación sigue el mismo orden |
| 1.3.4 Orientación | AA | Cumple | Revisión: la interfaz no bloquea la orientación; las pruebas en celular pasan |
| 1.3.5 Identificar el propósito de la entrada | AA | Cumple | Corregido en este sprint: `autoComplete` `username`, `current-password` y `one-time-code`; prueba de Playwright |
| 1.4.1 Uso del color | A | Cumple | El nivel de congestión se escribe («Congestión moderada · hora punta») y las entregas usan símbolo y texto, no solo color; prueba de Playwright |
| 1.4.3 Contraste mínimo | AA | Cumple | Lighthouse (`color-contrast`): accesibilidad 100 en las 6 pantallas, en móvil y escritorio, y en el tema oscuro y el tema claro (24 mediciones) |
| 1.4.4 Cambio de tamaño del texto | AA | Cumple | Pruebas de Playwright con una ventana de 640 px, que equivale a ampliar al 200 % una de 1280 px: sin desbordamiento horizontal |
| 1.4.10 Reflujo | AA | Cumple | Pruebas de Playwright con 320 px de ancho: mapa, rutas y sostenibilidad sin desplazamiento horizontal; además las pantallas del celular |
| 1.4.11 Contraste de los componentes no textuales | AA | No verificado | Lighthouse no lo mide; no se revisó el contraste de los bordes de los campos ni de las marcas del mapa |
| 1.4.12 Espaciado del texto | AA | Cumple | Prueba de Playwright con el espaciado que pide WCAG (interlineado 1.5, letras 0.12 em, palabras 0.16 em): no se desborda ni se pierde contenido |
| 1.4.13 Contenido al pasar el mouse o enfocar | AA | Cumple | Revisión: la ayuda («i») aparece al pasar el mouse o enfocar, se cierra con Escape y no tapa el campo |
| 2.1.1 Teclado | A | Parcial | Todo se opera con el teclado salvo los marcadores del mapa de Leaflet, que no reciben el foco; la misma información está en las listas del panel |
| 2.1.2 Sin trampas de teclado | A | Cumple | Prueba de Playwright: los diálogos se cierran con Escape y el foco no queda atrapado |
| 2.1.4 Atajos de teclado de una tecla | A | No aplica | El sistema no define atajos de una tecla |
| 2.2.1 Tiempo ajustable | A | Parcial | Los avisos emergentes desaparecen a los 3.5 s; el resultado de cada acción queda también en pantalla |
| 2.2.2 Pausar, detener, ocultar | A | Cumple | La actualización automática del mapa cada 30 s se activa y desactiva con una casilla |
| 2.3.1 Umbral de tres destellos | A | Cumple | No hay contenido que parpadee |
| 2.4.1 Evitar bloques | A | Cumple | Corregido en este sprint: enlace «Saltar al contenido»; prueba de Playwright con el primer Tab y Enter |
| 2.4.2 Página titulada | A | Cumple | Corregido en este sprint: cada sección tiene su título («Mapa · RouteZero»); prueba de Playwright |
| 2.4.3 Orden del foco | A | Cumple | Revisión: el foco sigue el orden visual; los dos `autoFocus` se reemplazaron por enfoque por código al aparecer el campo |
| 2.4.4 Propósito de los enlaces | A | Cumple | Lighthouse (`link-name`): todos los enlaces y botones tienen nombre |
| 2.4.6 Encabezados y etiquetas | AA | Cumple | Corregido en este sprint: la pantalla del mapa no tenía título `h1` y ahora lo tiene para los lectores de pantalla; prueba de Playwright |
| 2.4.7 Foco visible | AA | Cumple | Corregido en este sprint: contorno de 2 px con `:focus-visible`; prueba de Playwright |
| 2.4.11 Foco no oculto (mínimo) — nuevo en 2.2 | AA | Cumple | Revisión: no hay encabezados ni barras fijas que tapen el elemento enfocado |
| 2.5.1 Gestos del puntero | A | Cumple | El zoom del mapa también se hace con botones; ninguna acción exige gestos de varios dedos |
| 2.5.3 Etiqueta en el nombre | A | Cumple | Revisión: el nombre accesible de cada botón contiene su texto visible |
| 2.5.7 Movimientos de arrastre — nuevo en 2.2 | AA | Cumple | Arrastrar el mapa tiene alternativa con botones de zoom y teclas de flecha; elegir una ubicación se hace con un clic |
| 2.5.8 Tamaño del objetivo (mínimo) — nuevo en 2.2 | AA | Cumple | Los controles miden más de 24 px y los de la vista del conductor, al menos 44 px (prueba de Playwright) |
| 3.1.1 Idioma de la página | A | Cumple | Lighthouse (`html-has-lang`): `lang="es"` |
| 3.2.1 Al recibir el foco | A | Cumple | El foco no dispara cambios de contexto |
| 3.2.2 Al introducir datos | A | Cumple | Los formularios solo se envían con el botón |
| 3.2.3 Navegación coherente | AA | Cumple | El mismo menú lateral, en el mismo orden, en todas las pantallas de operaciones |
| 3.2.6 Ayuda coherente — nuevo en 2.2 | A | No aplica | El sistema no tiene un mecanismo de ayuda repetido entre páginas; la ayuda contextual «i» es uniforme |
| 3.3.1 Identificación de errores | A | Cumple | Los errores se muestran como texto y no solo con color; corregido en este sprint: los 17 mensajes de error en línea llevan `role="alert"`; prueba de Vitest |
| 3.3.2 Etiquetas o instrucciones | A | Cumple | Cada campo tiene su etiqueta y, en los de datos técnicos, una ayuda que explica qué escribir |
| 3.3.3 Sugerencia ante errores | AA | Parcial | Los mensajes del sistema sugieren qué hacer («Seleccione otro periodo»), pero los errores de validación genéricos de la API solo indican el campo |
| 3.3.4 Prevención de errores | AA | Cumple | Eliminar, cancelar y confirmar rutas piden confirmación en un diálogo |
| 3.3.7 Entrada redundante — nuevo en 2.2 | A | Cumple | Ningún formulario vuelve a pedir un dato ya escrito |
| 3.3.8 Autenticación accesible (mínimo) — nuevo en 2.2 | AA | Cumple | El acceso no exige resolver acertijos; se puede pegar y autocompletar, también el código de 6 dígitos (`one-time-code`) |
| 4.1.2 Nombre, función, valor | A | Cumple | Lighthouse y W3C (0 errores): elementos nativos y atributos ARIA válidos |
| 4.1.3 Mensajes de estado | AA | Cumple | Corregido en este sprint: los avisos usan `<output>` o `role="status"` y los errores `role="alert"`, que los lectores de pantalla anuncian sin mover el foco |

## 4. Cómo repetir la evaluación

Desde `frontend/`:

- `npm run auditar`: Lighthouse y validador W3C de las 6 pantallas, con datos sintéticos (el W3C llama al servicio público).
- `TEMA=claro npm run auditar`: lo mismo con el tema claro.
- `npm run test:e2e`: las 33 pruebas de extremo a extremo, incluidas las de accesibilidad de `e2e/accesibilidad.spec.ts`; `npm test` corre las 100 de Vitest.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-26 | Versión inicial: evaluación de WCAG 2.2 nivel AA con mediciones automáticas, pruebas de Playwright, hallazgos y correcciones | Inciso Aguilar Elizabeth Antonela |
