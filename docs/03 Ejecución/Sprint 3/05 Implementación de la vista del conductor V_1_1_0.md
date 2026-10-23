# 05 Implementación de la Vista del Conductor

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 3 — Rutas y Visualización (17 oct – 30 oct 2026) |
| **Ítem** | HU-014 (Visualizar ruta asignada en modo conductor) |
| **Fecha** | 2026-10-20 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../README.md)

---

Este documento registra cómo se implementó la vista del conductor (HU-014): qué ve, cómo se vincula su cuenta con su ficha de conductor, qué puede hacer y qué pruebas la respaldan. Reutiliza el trazado por calles y la congestión por horas punta de [`04 Implementación del mapa de rutas`](04%20Implementaci%C3%B3n%20del%20mapa%20de%20rutas%20V_1_2_0.md).

## 1. Qué hace

- **Escenario 1 (con ruta asignada):** al entrar con una cuenta de rol CONDUCTOR, la pantalla muestra **únicamente su ruta de hoy**: su recorrido por calles, sus paradas pendientes, la siguiente parada y las alertas de tráfico, en formato simplificado y pensado primero para el celular.
- **Escenario 2 (sin ruta asignada):** muestra el mensaje «No tienes rutas asignadas por el momento.» sin mapa.
- **Registro de entregas:** el conductor marca cada parada como **Entregado** o **No se pudo** (entrega fallida), con una confirmación previa porque no se puede deshacer.
- **Monitoreo:** la pantalla vuelve a pedir su ruta cada 30 s (el despacho puede re-optimizarla mientras el conductor circula) y tiene un botón Actualizar.
- Solo ve rutas **confirmadas, en ejecución o completadas**: nunca un borrador.

## 2. Vínculo entre la cuenta y el conductor

Hasta ahora la tabla `conductores` tenía la columna `usuario_id` (opcional y única), pero nada la llenaba. El vínculo se hace **por correo y de forma automática**:

1. La primera vez que un conductor abre su vista, el sistema busca el conductor sin usuario cuyo correo coincide (sin distinguir mayúsculas) con el correo de la cuenta con la que inició sesión.
2. Si lo encuentra, guarda `usuario_id` y registra en la auditoría la acción `conductor_vinculado`. Desde entonces ya no necesita el correo.
3. Si no lo encuentra, la pantalla explica que la cuenta no está vinculada y pide al administrador que registre el correo en la ficha del conductor.

Para vincular a un conductor, el administrador solo debe registrar en su ficha **el mismo correo con el que inicia sesión**. No hace falta una pantalla nueva ni listar usuarios (que exigiría leer el esquema de autenticación de Supabase).

## 3. API

| Método y ruta | Rol | Qué hace |
|---|---|---|
| `GET /api/rutas/mi-ruta` | Conductor | La ruta del conductor en la fecha (por defecto hoy): paradas, recorrido, siguiente parada, entregadas, pendientes y alertas. Parámetros opcionales `fecha` y `hora` (para pruebas y demostraciones). |
| `PATCH /api/rutas/{ruta}/paradas/{pedido}/entrega` | Administrador, Operador y ahora **Conductor** | El conductor solo puede registrar las entregas de **su propia ruta**: en otra responde 403, igual que si su cuenta no está vinculada. |

Un conductor no tiene acceso al mapa general, a la re-optimización, a los incidentes ni a las rutas de otros (RN-014, mínimo privilegio): la respuesta de `mi-ruta` solo contiene datos suyos.

## 4. Alertas de tráfico

- Se muestran las vías de la RN-012 que a la hora actual están en **amarillo o rojo** (por hora punta, por un incidente o por ambos); si están en verde no se muestran.
- Cada alerta indica si **está en su ruta**. Para saberlo se comparan los nodos del grafo por los que pasa el recorrido del conductor (sin simplificar) con los nodos de cada vía; la línea que se dibuja sí está simplificada y perdería esos nodos, por eso el servicio usa los originales y no los expone.
- Solo las alertas que están en su ruta traen la geometría de la vía, para marcarla en el mapa; las demás no la envían.
- Se ordenan primero las que están en su ruta y, dentro de ellas, las rojas.

## 5. Pantalla (`ConductorPage`)

Reemplaza la vista previa con datos de ejemplo del Sprint 1.

- **Cabecera:** saludo con el nombre del conductor y estado de la actualización («Cargando tu ruta…», «Actualizando…» o la hora de la última).
- **Resumen:** «N de M entregas», horario de la ruta y barra de avance accesible.
- **Alertas de tráfico:** con la etiqueta «En tu ruta».
- **Mapa:** recorrido por calles, paradas numeradas con su estado (✓ entregada, ✗ fallida, ✕ cancelada), la siguiente parada destacada, el depósito y las vías en su ruta.
- **Siguiente parada:** cliente, hora estimada, retraso, peso, prioridad (EXPRESS se señala) y los botones Entregado y No se pudo.
- **Listas:** «Después» (las que faltan), «Cancelados: no los atiendas» (pedidos cancelados que siguen en su ruta hasta que el despacho re-optimice) y «Atendidas».
- **Estados vacíos:** cuenta sin vincular, sin ruta por ahora y ruta completada.
- **Barra inferior:** Actualizar y Cerrar sesión.

Los pedidos cancelados no cuentan como pendientes ni se ofrecen como siguiente parada.

## 6. Decisiones y limitaciones

| Decisión | Motivo |
|---|---|
| Vínculo automático por correo | Sin pantalla nueva ni acceso a la tabla de usuarios de autenticación; el administrador solo registra el correo. |
| El conductor registra sus propias entregas | La historia pide que complete su jornada; se restringe a su ruta. |
| Refresco automático cada 30 s, sin websockets | Suficiente para ver una re-optimización a tiempo y mucho más simple. |
| Confirmación en ambos botones | Un toque equivocado no se puede deshacer porque la API solo cambia paradas pendientes. |

Limitaciones:

- El vínculo depende de que el correo de la ficha coincida con el de la cuenta; no hay una pantalla para asignarlo a mano ni para corregirlo si el correo cambia.
- Una entrega fallida deja el pedido `ASIGNADO` y no se re-planifica sola (misma limitación de HU-012).
- El conductor ve solo su ruta de la fecha; no hay historial de jornadas anteriores.
- Falta medir el rendimiento de Lighthouse en producción (con la API simulada la vista da 96 en móvil; ver [`06 Calidad de la interfaz y pruebas de extremo a extremo`](06%20Calidad%20de%20la%20interfaz%20y%20pruebas%20de%20extremo%20a%20extremo%20V_1_0_0.md)).

## 7. Hallazgo: cuenta conductora rechazada por `token_version`

Al probar la API con la cuenta `conductor.prueba@routezero.dev`, **todos los endpoints respondían 401 «Token revocado»**. La causa: en la tabla `usuarios` esa cuenta tenía `token_version = 2` por pruebas anteriores, mientras Supabase seguía emitiendo tokens con `ver = 1`. Es el riesgo ya descrito en el diseño de autenticación (el Custom Access Token Hook parece cachear la versión). Se restableció a 1 igual que hace el helper de pruebas con la cuenta de administrador. Queda anotado porque un conductor real con ese desajuste quedaría bloqueado.

## 8. Pruebas

| Capa | Archivo | Qué comprueba |
|---|---|---|
| Servicio y API (base real) | `tests/test_conductor.py` (13) | Cuenta sin conductor, vínculo por correo sin distinguir mayúsculas y persistente, su ruta con paradas y siguiente, aislamiento entre conductores, borrador no visible, sin ruta ese día, avance hasta completar la ruta, entregas ajenas y de cuentas sin vínculo rechazadas (403), pedidos cancelados, alertas sin congestión y en hora punta, la vía que cruza la ruta, y roles. |
| Trazado | `tests/test_trazado.py` | Nodos del recorrido y nodos de una calle. |
| Frontend | `ConductorPage.test.tsx` (15) | Cuenta sin vincular, sin ruta, su ruta, express, registro de entregas con confirmación, cancelar la confirmación, avance, ruta completada, pedidos cancelados, alertas, refresco automático, error y cerrar sesión. |

Resultados al 20-10-2026:

- Frontend: **89 pruebas pasan** y el `npm run build` completo termina sin errores.
- Backend: la suite completa pasa con **328 pruebas y 98 % de cobertura** (24 min), incluidas las 13 del conductor; el detalle está en [`03 Estrategia y resultados de pruebas`](03%20Estrategia%20y%20resultados%20de%20pruebas%20V_1_5_0.md).
- La pantalla se revisó a mano en local con una ruta de demostración de hoy (6 paradas, dos de ellas sobre Av. Ferrocarril y Calle Real) y se vio correcta. El script `backend/tests_manual/demo_conductor.py` crea y borra esos datos (local y no versionado).
- Medida en Render el 22-10-2026 con una ruta de demostración de 6 paradas: **3.8 s la primera petición** (vincula la cuenta, calcula el recorrido por calles y llena la caché) y **2.6 s desde la caché**, con 49 KB; casi todo es la latencia base de ~2 s por petición (IMP-016). A las 08:30 la respuesta traía 3 alertas, todas en su ruta; a las 10:00, ninguna. El script es `backend/tests_manual/medir_mi_ruta_render.py` (local y no versionado).
- Lighthouse y W3C el 22-10-2026: accesibilidad, buenas prácticas y SEO en 100 y 0 errores de HTML, con y sin ruta; y pruebas de extremo a extremo en el viewport de un celular, sin desplazamiento horizontal y con botones de al menos 44 px (ver [`06 Calidad de la interfaz y pruebas de extremo a extremo`](06%20Calidad%20de%20la%20interfaz%20y%20pruebas%20de%20extremo%20a%20extremo%20V_1_0_0.md)).

---

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-20 | Versión inicial: vista del conductor (HU-014), vínculo por correo, API, alertas, pantalla, decisiones, hallazgo del token y pruebas | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-22 | Se agregan la medición en Render, Lighthouse, W3C y las pruebas de extremo a extremo en el celular | Inciso Aguilar Elizabeth Antonela |
