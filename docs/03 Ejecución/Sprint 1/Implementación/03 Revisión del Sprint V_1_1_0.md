# 03 Revisión del Sprint

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19-09-2026 – 02-10-2026) |
| **Fecha de la revisión** | 2026-10-02 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../../README.md)

---

## Historias de Usuario completadas en este Sprint

Las 13 historias comprometidas (8 Historias de Usuario + 5 Historias Técnicas, 42/42 Story Points) se completaron al 100 %. Detalle completo del avance verificado por ítem en [`01 Sprint 1 Plan de ejecución y estado V_1_5_0.md`](../01%20Sprint%201%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_5_0.md).

| ID | Historia de Usuario | Épica | SP |
|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema (login + MFA en dos pasos) | EP-01 Autenticación | 3 |
| HU-002 | Acceder solo a módulos permitidos por rol | EP-01 Autenticación | 3 |
| HU-003 | Registrar vehículo en la flota | EP-02 Flota | 3 |
| HU-004 | Editar datos de un vehículo | EP-02 Flota | 2 |
| HU-005 | Consultar disponibilidad de la flota | EP-02 Flota | 2 |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | EP-03 Pedidos | 3 |
| HU-007 | Registrar pedido con punto de referencia | EP-03 Pedidos | 2 |
| HU-008 | Cancelar pedido pendiente | EP-03 Pedidos | 2 |
| HT-01 | Autenticación JWT y protección OWASP Top 10 | EP-01 Autenticación | 8 |
| HT-02 | Cifrado de datos y cumplimiento de la Ley N° 29733 | EP-01 Autenticación | 5 |
| HT-03 | Infraestructura de despliegue en Render y Vercel | EP-01 Autenticación | 5 |
| HT-04 | Pruebas unitarias del módulo de flota | EP-02 Flota | 2 |
| HT-05 | Pruebas unitarias del módulo de pedidos | EP-03 Pedidos | 2 |

**Trabajo adicional no comprometido explícitamente en el sprint** (gestionado como el cambio OpenSpec `add-mfa-sesiones`, archivado): autenticación multifactor (MFA) con TOTP y gestión segura de sesiones (listar, revocar, renovación con detección de robo de sesión), más un módulo mínimo `clientes/` como prerrequisito de `pedidos/`.

## Demostración del trabajo completado

Demostración a los stakeholders de las funcionalidades implementadas, realizada sobre el sistema corriendo **en producción** (no solo en local):

- **Backend en Render**: [`routezero-7k7j.onrender.com`](https://routezero-7k7j.onrender.com), con `/api/health` y login verificados en vivo contra Supabase real.
- **Frontend en Vercel**: [`route-zero-omega.vercel.app`](https://route-zero-omega.vercel.app).
- **Flujo demostrado**: login con verificación MFA en dos pasos → redirección automática según el rol devuelto por `/api/auth/me` (Administrador/Operador ven el panel completo; Conductor recibe una vista propia mobile-first) → gestión de flota (alta, edición de estado, filtrado por disponibilidad) → registro de pedidos con selección de cliente y mapa real de Huancayo (Leaflet + OpenStreetMap) → cancelación de un pedido pendiente → pantalla de sesiones activas con revocación individual y masiva.
- **Documentación de API**: los 9 endpoints de autenticación, 3 de flota, 5 de pedidos/clientes y 1 de auditoría, documentados en Swagger (`/docs`).

## Pendientes

- Nueva versión de [`11. Base de datos`](../../../01%20Inicio/11.%20Base%20de%20datos%20V_1_4_0.md) que documente los módulos de flota, clientes y pedidos (ya implementados, pero el documento aún no los refleja).
- Ampliar la cobertura de pruebas automatizadas del frontend (Jest/Vitest) a los módulos de Flota y Pedidos — hoy solo cubre los componentes de MFA.
- Ejecutar y documentar auditorías de Lighthouse (≥ 90) y validación W3C sobre el frontend desplegado.
- Resolver IMP-006 (posible caché del `token_version` en el Custom Access Token Hook de Supabase) — ver [`02 Registro de Impedimentos`](02%20Registro%20de%20Impedimentos%20V_1_0_0.md).
- Motor de optimización de rutas (VRPTW + Green VRP con ACO) y módulo de conductores, planificados para el Sprint 2.
- Mejorar la captura de coordenadas en el registro de pedidos: reemplazar el ingreso manual de latitud/longitud por un buscador de direcciones con geocodificación (Nominatim/OpenStreetMap) más la posibilidad de ajustar el punto sobre el mapa, detectado como hueco de usabilidad durante la demostración interna.

---

[← Volver al README Principal](../../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-02 | Versión inicial: revisión del Sprint 1 con las 13 historias completadas, resumen de la demostración en producción y los pendientes para el Sprint 2 | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-10-02 | Se agrega a "Pendientes" la mejora de usabilidad detectada en el registro de pedidos (captura manual de lat/lng) | Inciso Aguilar Elizabeth Antonela |
