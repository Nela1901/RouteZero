# 02 Registro de Impedimentos

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03-10-2026 – 16-10-2026) |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

La numeración continúa la del [Registro del Sprint 1](../../Sprint%201/Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_1_0.md) (IMP-001 a IMP-006).

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-005 | 2026-09-20 | *(Arrastrado del Sprint 1)* Disponibilidad limitada de los integrantes por carga académica (RSK-005): la implementación se concentró casi por completo en un solo integrante, sin que el resto tomara módulos propios | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-16 | Abierto | — | En el Sprint 2 cada ítem tiene responsable en Jira y el equipo declara que sus integrantes colaboraron (revisión de la HU-009, apoyo en la HU-011 y HU-010; ver «Aporte por integrante» en la Revisión del Sprint), aunque los commits salen de una sola cuenta de GitHub. Queda el checkpoint de medio sprint del 10-10-2026 para detectar atrasos a tiempo |
| IMP-007 | 2026-10-05 | En las pruebas de Flota el filtro por estado demoraba en responder. Cada cambio de filtro hacía una petición a la API, que a su vez abre dos sesiones contra la base remota en Supabase (verificación del usuario y sesión con RLS), con varios viajes de red por petición. Impacto: interfaz lenta en una lista de pocos registros | Media | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | La pantalla de Flota carga la lista completa una sola vez y filtra en el navegador, por lo que cambiar de filtro es instantáneo. Queda como mejora en HT-08 reducir los viajes por petición del backend (reutilizar la sesión de base de datos del usuario) |
| IMP-008 | 2026-10-05 | El registro de vehículos fallaba sin explicación visible: ante un error de validación (HTTP 422) la API devuelve una lista de objetos y la interfaz la mostraba como `[object Object]`. Los campos numéricos tampoco indicaban el paso decimal permitido, por lo que valores con más decimales que los admitidos eran rechazados. El backend se verificó sin cambios con `e2e_flota.py` (11/11) | Alta | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | Se agregó `mensajeDeError` en `frontend/src/api/client.ts`, que convierte el detalle de la API en un texto con el campo y el motivo; se aplicó a Flota y Pedidos. Los campos numéricos declaran su paso (`step`) y la placa se normaliza (espacios fuera, mayúsculas) antes de enviarse |
| IMP-009 | 2026-10-05 | La sección "Flota" aparecía en el menú del rol Operador aunque la API le responde 403 por RN-014, mostrando una pantalla vacía y confusa | Media | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | El menú filtra los ítems según el rol (`roles` en `OperacionesLayout.tsx`) y la ruta `/app/flota` solo se registra para el Administrador (`App.tsx`) |
| IMP-010 | 2026-10-05 | La medición en Render gratuito mostró que generar rutas con 150 pedidos tardaba 64 s (límite: 45 s). El perfilado reveló que el tiempo se iba en guardar el resultado fila por fila, con cada INSERT como un viaje a la base remota. Impacto: incumplía el escenario 1 de HU-011 | Alta | Equipo | 2026-10-05 | Resuelto | 2026-10-05 | La persistencia pasó a INSERT en bloque y se reservan 5 s del presupuesto de tiempo para guardar; la generación mide 29.1 s en Render (150 pedidos, 15 vehículos) |
| IMP-011 | 2026-10-05 | Un vehículo o conductor ya comprometido en una ruta confirmada podía asignarse otra vez a otra ruta de la misma fecha (doble asignación), generando rutas imposibles de cumplir | Alta | Equipo | 2026-10-05 | Resuelto | 2026-10-05 | La generación excluye los vehículos y conductores de rutas CONFIRMADA o EN_EJECUCION de la misma fecha; se agregaron pruebas de doble asignación y el requisito en la especificación de `route-planning` |
| IMP-012 | 2026-10-05 | Render gratuito no muestra métricas de memoria ni de CPU (solo en planes de pago), por lo que no se podía comprobar que el motor cupiera en los 512 MB ni qué parte del tiempo era cómputo | Media | Equipo | 2026-10-05 | Resuelto | 2026-10-05 | La respuesta de generar incluye `tiempos` por etapa y `memoria_pico_mb`; medido: 199 a 210 MB de 512 MB |
| IMP-013 | 2026-10-05 | La CPU compartida de Render gratuito (0.1 vCPU) hace lento el cálculo: las matrices de distancias toman 8.3 a 8.8 s y el ACO completa solo 8 o 9 iteraciones dentro del presupuesto, por lo que la mejora sobre la solución voraz es modesta | Media | Equipo | 2026-10-16 | Abierto | — | Dentro del límite (29.1 s de 45 s). Mitigado con el presupuesto de tiempo del motor y la solución voraz como base; queda como optimización opcional calcular las matrices con un único Dijkstra. Pasar a un plan con más CPU lo eliminaría |
| IMP-014 | 2026-10-05 | La documentación citaba el «DS 033-2012-MTC», que no existe: la norma vigente de límites de velocidad es el DS 033-2001-MTC (Reglamento Nacional de Tránsito). Impacto: cita normativa errónea en documentos que se presentan al docente | Media | Equipo | 2026-10-05 | Resuelto | 2026-10-05 | Se verificó contra el texto oficial y se corrigió la cita en los documentos; se agrega la verificación de normas citadas al proceso de revisión |
| IMP-015 | 2026-10-05 | Correr toda la suite de pruebas mientras se medía contra la misma cuenta de pruebas hacía fallar mediciones (401 «sesión revocada») y cuatro pruebas de sesiones, porque `test_sesiones` y `test_mfa` borran las sesiones de esa cuenta | Baja | Equipo | 2026-10-05 | Resuelto | 2026-10-05 | Falsos fallos, no defectos: se repitieron por separado (16 aprobadas). Regla de proceso: no ejecutar pruebas y mediciones a la vez con la cuenta de pruebas |
| IMP-016 | 2026-10-06 | Cada petición a la API tarda cerca de 1 s en Render gratuito por los varios viajes a la base remota de Supabase. En Lighthouse esto deja el rendimiento de Mapa (88-89) y Pedidos (85, escritorio) por debajo de 90, con LCP de hasta 2.8 s, aunque el hilo principal no se bloquea (TBT 0 ms) ni hay desplazamientos de diseño (CLS 0) | Media | Equipo | 2026-10-16 | Abierto | — | No es defecto del frontend. Mitigación posible: reutilizar la sesión de base de datos por petición y agrupar consultas (ya listado como mejora en IMP-007); un plan de pago o una región más cercana a Supabase también lo reduciría |
| IMP-017 | 2026-10-06 | Al paginar `GET /api/pedidos` el mapa dejó de funcionar en producción (`e.map is not a function`), porque seguía esperando una lista. Lo detectó la auditoría de consola de Lighthouse; ninguna prueba cubría el mapa | Alta | Equipo (auditoría Lighthouse) | 2026-10-06 | Resuelto | 2026-10-06 | El mapa lee `items` pidiendo la página máxima (`limite=200`) y se agregó `MapaPage.test.tsx`. Lección de proceso: al cambiar un contrato de la API se buscan todos sus consumidores |
---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: IMP-005 arrastrado del Sprint 1 y registro de IMP-007, IMP-008 e IMP-009 detectados al probar Flota | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-06 | Se registran IMP-010 a IMP-017 (rendimiento de persistencia, doble asignación, falta de métricas en Render, CPU limitada, cita normativa errónea, interferencia entre pruebas y mediciones, latencia de la API y regresión del mapa) y se actualiza IMP-005 | Inciso Aguilar Elizabeth Antonela |
