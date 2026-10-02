# 01 Sprint 1 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19 sep – 02 oct 2026) |
| **Fecha de corte** | 2026-09-27 |
| **Inspección** | 2026-10-02 |
| **Versión** | 1.1.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)):

> *Implementar la base del sistema RouteZero: autenticación JWT con control de acceso por roles (EP-01), gestión de flota de vehículos (EP-02) y registro de pedidos con coordenadas GPS (EP-03).*

El sprint compromete **13 ítems y 42 Story Points** (8 Historias de Usuario y 5 Historias Técnicas). Este documento registra el estado real de cada ítem a la fecha de corte y el plan para cerrar el sprint antes de la inspección.

## 2. Alcance comprometido y estado al 27-09-2026

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem está implementada y verificada) y **Pendiente** (sin implementación).

| ID | Título | Épica | SP | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema | EP-01 | 3 | Parcial | API completa: `POST /api/auth/login`, bloqueo tras 3 intentos por 15 min con tiempo restante (RN-001), respuesta genérica exista o no el correo | Pantalla de inicio de sesión y redirección al módulo según el rol (frontend) |
| HU-002 | Acceder solo a módulos permitidos por rol | EP-01 | 3 | Parcial | Autorización por rol en la API: `requiere_rol(*roles)` protege flota y pedidos (403 para un rol sin permiso); todo endpoint protegido exige además sesión válida y activa (401 sin token o con token falso); RLS a nivel de base de datos | Reflejo de la autorización por rol en la interfaz (frontend) |
| HU-003 | Registrar vehículo en la flota | EP-02 | 3 | Completada | `POST /api/vehiculos`, rechazo de placa duplicada (409), solo rol ADMINISTRADOR | — |
| HU-004 | Editar datos de un vehículo | EP-02 | 2 | Completada | `PUT /api/vehiculos/{id}`, 404 si el vehículo no existe | — |
| HU-005 | Consultar disponibilidad de la flota | EP-02 | 2 | Completada | `GET /api/vehiculos` con filtro opcional por estado | — |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | EP-03 | 3 | Completada | `POST /api/pedidos`, validación de zona de cobertura de Huancayo (RN-007) y de existencia del cliente, rechazo de ventana de tiempo invertida | — |
| HU-007 | Registrar pedido con punto de referencia | EP-03 | 2 | Completada | Cubierta por diseño: el campo `referencia` del pedido siempre fue texto libre, sin distinguir dirección formal de punto de referencia | — |
| HU-008 | Cancelar pedido pendiente | EP-03 | 2 | Completada | `DELETE /api/pedidos/{id}` solo si el pedido está `PENDIENTE`; 409 si ya fue asignado a una ruta o ya estaba cancelado, 404 si no existe | — |
| HT-01 | Autenticación JWT y protección OWASP Top 10 | EP-01 | 8 | Parcial | JWT firmado por Supabase Auth y verificado con llave pública (ES256), con tolerancia de reloj (`leeway`); autorización por rol (`requiere_rol`); consultas SQL parametrizadas y validación con Pydantic; CORS restrictivo; RLS; Swagger en `/docs` | Registro de eventos de seguridad en `logs_auditoria`, prueba explícita de inyección SQL, análisis estático (CodeQL o SonarQube) |
| HT-02 | Cifrado de datos y cumplimiento de la Ley N° 29733 | EP-01 | 5 | Pendiente | Ningún dato sensible de conductores se almacena todavía | Registro del consentimiento explícito (RN-013) y verificación del cifrado en reposo del proveedor |
| HT-03 | Infraestructura de despliegue en Render y Vercel | EP-01 | 5 | Pendiente | Base de datos ya alojada en Supabase | Despliegue del backend en Render y del frontend en Vercel |
| HT-04 | Pruebas unitarias del módulo de flota | EP-02 | 2 | Parcial | Verificado de extremo a extremo (registro, placa duplicada, edición, 404, listado filtrado, rechazo por rol) | Incorporar los casos a `backend/tests/` con pytest y medir cobertura |
| HT-05 | Pruebas unitarias del módulo de pedidos | EP-03 | 2 | Parcial | Verificado de extremo a extremo (17 casos: zona de cobertura, cliente inexistente, ventana invertida, filtros, las tres transiciones de cancelación) | Incorporar los casos a `backend/tests/` con pytest y medir cobertura |

**Resumen del corte:** de los 42 SP comprometidos, **17 SP están completados** (HU-003 a HU-008), **21 SP tienen avance parcial** (HU-001, HU-002, HT-01, HT-04, HT-05) y 10 SP están pendientes (HT-02, HT-03).

## 3. Trabajo adicional al alcance comprometido

Durante el sprint se agregó una mejora de seguridad sobre EP-01, gestionada como el cambio OpenSpec `add-mfa-sesiones` (ver [`openspec/changes/add-mfa-sesiones/`](../../../openspec/changes/add-mfa-sesiones/)):

- **Autenticación multifactor (MFA) con TOTP** como segundo factor del inicio de sesión.
- **Gestión segura de sesiones**: listar, revocar una o todas, renovación con detección de robo de sesión.

También se agregó un módulo mínimo `clientes/` (registrar y listar) como prerrequisito de `pedidos/`, no comprometido explícitamente en el sprint pero necesario para HU-006. El alcance completo de HU-010 (preferencias de entrega del cliente) queda para su propio sprint (EP-04).

**Justificación.** RouteZero maneja datos personales de conductores y clientes protegidos por la Ley N° 29733, y los roles con mayor privilegio (Administrador, Gerente) no deberían depender de una sola contraseña. El detalle técnico está en [`02 Implementación del módulo de autenticación`](02%20Implementaci%C3%B3n%20del%20m%C3%B3dulo%20de%20autenticaci%C3%B3n%20V_1_0_0.md).

**Estado:** el backend de los tres módulos (autenticación con MFA y sesiones, flota, pedidos) está completo y verificado de extremo a extremo — **65 de 65 comprobaciones**; faltan las pantallas del frontend, la cobertura de pruebas con pytest-cov y el cierre documental.

## 4. Definition of Done — estado del backend

Criterios del DoD global ([`01 Transformando a ágil`](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md), sección 5):

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov y Jest | Pendiente (hay 65 comprobaciones de extremo a extremo en `backend/tests_manual/`, ver documento 03; falta incorporarlas a `backend/tests/` y medir cobertura) |
| 2 | Análisis estático | 0 vulnerabilidades críticas (CodeQL o SonarQube) | Pendiente |
| 3 | Revisión de código | Pull Request aprobado antes del merge a `main` | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints documentados en Swagger/OpenAPI | Cumplido para los 9 endpoints de autenticación, 3 de flota y 5 de pedidos/clientes (`/docs`) |
| 6 | Criterios de aceptación verificados | Escenarios ejecutados y aprobados | Cumplido en el backend para HU-003 a HU-008 y `specs/mfa-totp`/`specs/session-management`; pendiente en HU-001 y HU-002 hasta que exista interfaz |
| 7 | Cumplimiento de estándares | Sin errores W3C, Lighthouse ≥ 90, sin vulnerabilidades OWASP críticas | Parcial (ver mapeo OWASP en el documento 02); interfaz aún sin construir |
| 8 | Commit en rama e integración por Pull Request | Historia commiteada y integrada | Parcial (commiteado en `backend`, subido a `origin/backend`; Pull Request a `main` pendiente) |

## 5. Plan de cierre del Sprint (27-09 → 02-10)

Se cumplió por completo la meta del día 27-09 (flota y pedidos) y se adelantó parte del trabajo de autorización por rol que estaba planificado para el 28-09. Plan actualizado para los días restantes. **Está sujeta a validación del equipo.**

| Día | Fecha | Foco | Resultado verificable |
|---|---|---|---|
| ~~Dom~~ | ~~27-09~~ | ~~Backend de flota y de pedidos con validaciones, autorización por rol~~ | **Cumplido:** HU-003 a HU-008 completas, HT-04 y HT-05 verificadas de extremo a extremo |
| Lun | 28-09 | Registro de auditoría (`logs_auditoria`), consentimiento (RN-013), prueba de inyección SQL | HT-01 y HT-02 completas |
| Mar | 29-09 | Frontend base: proyecto React, inicio de sesión, MFA y sesiones | HU-001 completa |
| Mié | 30-09 | Frontend de flota y pedidos, control de acceso por rol en la interfaz | HU-002, HU-003 a HU-008 de extremo a extremo |
| Jue | 01-10 | Cobertura con pytest-cov, incorporación de los casos de `tests_manual/` a `backend/tests/`, despliegue en Render y Vercel, Pull Request y etiqueta `v0.1.0` | HT-03, HT-04, HT-05, DoD |
| Vie | 02-10 | Inspección | Demostración del sprint |

**Orden de recorte si el tiempo no alcanza** (de lo primero que se sacrificaría a lo último): (1) despliegue en la nube (HT-03), que se reemplazaría por una demostración local documentada; (2) pantallas de MFA y sesiones, manteniendo el inicio de sesión; (3) HT-02. La gestión de flota y de pedidos, con el acceso por rol, ya está asegurada como núcleo del sprint.

## 6. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Días de trabajo restantes hasta la inspección concentrados en el frontend (aún sin empezar) | No cerrar el sprint completo | Plan diario de la sección 5 y orden de recorte |
| Primer contacto del equipo con React en este proyecto | Retrasos en las pantallas | Pantallas mínimas y reutilización de componentes; verificación manual diaria |
| Despliegue en Render y Vercel depende de cuentas y variables de entorno | HT-03 fuera del sprint | Demostración local como alternativa documentada |
| Cambios de diseño descubiertos al probar contra el proveedor de identidad | Retrabajo | Registro de cambios y pruebas de extremo a extremo antes de construir sobre cada pieza |

## 7. Evidencias

- Cambio OpenSpec `add-mfa-sesiones`: [`proposal.md`](../../../openspec/changes/add-mfa-sesiones/proposal.md), [`design.md`](../../../openspec/changes/add-mfa-sesiones/design.md), [`tasks.md`](../../../openspec/changes/add-mfa-sesiones/tasks.md).
- Código del backend: [`backend/`](../../../backend/), módulos `auth/`, `flota/`, `clientes/` y `pedidos/`.
- Scripts de verificación de extremo a extremo: `backend/tests_manual/` (`e2e_sesiones.py`, `e2e_flota.py`, `e2e_pedidos.py`).
- Plan y resultados de pruebas: [`03 Plan y resultados de pruebas`](03%20Plan%20y%20resultados%20de%20pruebas%20V_1_0_0.md).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-09-26 | Versión inicial: estado del Sprint 1 al 26-09-2026 y plan de cierre | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-09-27 | Estado al 27-09-2026: HU-003 a HU-008 completadas, autorización por rol (HU-002) implementada en la API, ajuste del plan de cierre | Inciso Aguilar Elizabeth Antonela |
