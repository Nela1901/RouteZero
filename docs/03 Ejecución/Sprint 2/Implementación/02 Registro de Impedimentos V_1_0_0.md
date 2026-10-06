# 02 Registro de Impedimentos

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03-10-2026 – 16-10-2026) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../../README.md)

---

La numeración continúa la del [Registro del Sprint 1](../../Sprint%201/Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_1_0.md) (IMP-001 a IMP-006).

| Impedimento # | Fecha de Registro | Descripción del Impedimento así como el Impacto en el Proyecto | Prioridad | Reportado por | Fecha tope de Resolución | Estado | Fecha de Resolución | Resolución/Comentarios |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-005 | 2026-09-20 | *(Arrastrado del Sprint 1)* Disponibilidad limitada de los integrantes por carga académica (RSK-005): la implementación se concentró casi por completo en un solo integrante, sin que el resto tomara módulos propios | Alta | Inciso Aguilar Elizabeth Antonela | 2026-10-16 | Abierto | — | En el Sprint 2 cada ítem tiene responsable en Jira; se agrega un checkpoint de medio sprint el 10-10-2026 para detectar atrasos a tiempo |
| IMP-007 | 2026-10-05 | En las pruebas de Flota el filtro por estado demoraba en responder. Cada cambio de filtro hacía una petición a la API, que a su vez abre dos sesiones contra la base remota en Supabase (verificación del usuario y sesión con RLS), con varios viajes de red por petición. Impacto: interfaz lenta en una lista de pocos registros | Media | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | La pantalla de Flota carga la lista completa una sola vez y filtra en el navegador, por lo que cambiar de filtro es instantáneo. Queda como mejora en HT-08 reducir los viajes por petición del backend (reutilizar la sesión de base de datos del usuario) |
| IMP-008 | 2026-10-05 | El registro de vehículos fallaba sin explicación visible: ante un error de validación (HTTP 422) la API devuelve una lista de objetos y la interfaz la mostraba como `[object Object]`. Los campos numéricos tampoco indicaban el paso decimal permitido, por lo que valores con más decimales que los admitidos eran rechazados. El backend se verificó sin cambios con `e2e_flota.py` (11/11) | Alta | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | Se agregó `mensajeDeError` en `frontend/src/api/client.ts`, que convierte el detalle de la API en un texto con el campo y el motivo; se aplicó a Flota y Pedidos. Los campos numéricos declaran su paso (`step`) y la placa se normaliza (espacios fuera, mayúsculas) antes de enviarse |
| IMP-009 | 2026-10-05 | La sección "Flota" aparecía en el menú del rol Operador aunque la API le responde 403 por RN-014, mostrando una pantalla vacía y confusa | Media | Equipo (pruebas del Sprint 1) | 2026-10-05 | Resuelto | 2026-10-05 | El menú filtra los ítems según el rol (`roles` en `OperacionesLayout.tsx`) y la ruta `/app/flota` solo se registra para el Administrador (`App.tsx`) |

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: IMP-005 arrastrado del Sprint 1 y registro de IMP-007, IMP-008 e IMP-009 detectados al probar Flota | Inciso Aguilar Elizabeth Antonela |
