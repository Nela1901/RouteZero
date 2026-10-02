# 01 Sprint 1 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19 sep – 02 oct 2026) |
| **Fecha de corte** | 2026-09-26 |
| **Inspección** | 2026-10-02 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)):

> *Implementar la base del sistema RouteZero: autenticación JWT con control de acceso por roles (EP-01), gestión de flota de vehículos (EP-02) y registro de pedidos con coordenadas GPS (EP-03).*

El sprint compromete **13 ítems y 42 Story Points** (8 Historias de Usuario y 5 Historias Técnicas). Este documento registra el estado real de cada ítem a la fecha de corte y el plan para cerrar el sprint antes de la inspección.

## 2. Alcance comprometido y estado al 26-09-2026

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem está implementada y verificada) y **Pendiente** (sin implementación).

| ID | Título | Épica | SP | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema | EP-01 | 3 | Parcial | API completa: `POST /api/auth/login`, bloqueo tras 3 intentos por 15 min con tiempo restante (RN-001), respuesta genérica exista o no el correo | Pantalla de inicio de sesión y redirección al módulo según el rol (frontend) |
| HU-002 | Acceder solo a módulos permitidos por rol | EP-01 | 3 | Parcial | Todo endpoint protegido exige sesión válida y activa (401 sin token o con token falso); RLS a nivel de base de datos | Autorización por rol (Administrador, Operador, Conductor) sobre cada módulo y su reflejo en la interfaz |
| HU-003 | Registrar vehículo en la flota | EP-02 | 3 | Pendiente | Tabla `vehiculos` diseñada en [`11. Base de datos`](../../01%20Inicio/11.%20Base%20de%20datos%20V_1_2_0.md) | Creación de la tabla, endpoints, validación de placa duplicada, pantalla |
| HU-004 | Editar datos de un vehículo | EP-02 | 2 | Pendiente | — | Endpoint de edición y pantalla |
| HU-005 | Consultar disponibilidad de la flota | EP-02 | 2 | Pendiente | — | Consulta filtrada por estado y pantalla |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | EP-03 | 3 | Pendiente | Tablas `clientes` y `pedidos` diseñadas | Creación de tablas, validación de zona de cobertura (RN-007), endpoints, pantalla |
| HU-007 | Registrar pedido con punto de referencia | EP-03 | 2 | Pendiente | — | Alta con referencia en lugar de dirección |
| HU-008 | Cancelar pedido pendiente | EP-03 | 2 | Pendiente | — | Cambio de estado con regla sobre pedidos ya asignados |
| HT-01 | Autenticación JWT y protección OWASP Top 10 | EP-01 | 8 | Parcial | JWT firmado por Supabase Auth y verificado con llave pública (ES256); consultas SQL parametrizadas y validación con Pydantic; CORS restrictivo; RLS; Swagger en `/docs` | Registro de eventos de seguridad en `logs_auditoria`, prueba explícita de inyección SQL, análisis estático (CodeQL o SonarQube) |
| HT-02 | Cifrado de datos y cumplimiento de la Ley N° 29733 | EP-01 | 5 | Pendiente | Ningún dato sensible de conductores se almacena todavía | Registro del consentimiento explícito (RN-013) y verificación del cifrado en reposo del proveedor |
| HT-03 | Infraestructura de despliegue en Render y Vercel | EP-01 | 5 | Pendiente | Base de datos ya alojada en Supabase | Despliegue del backend en Render y del frontend en Vercel |
| HT-04 | Pruebas unitarias del módulo de flota | EP-02 | 2 | Pendiente | — | Depende de HU-003 a HU-005 |
| HT-05 | Pruebas unitarias del módulo de pedidos | EP-03 | 2 | Pendiente | — | Depende de HU-006 a HU-008 |

**Resumen del corte:** de los 42 SP comprometidos, ningún ítem está completado; **14 SP tienen avance parcial** (HU-001, HU-002 y HT-01) y 28 SP están pendientes.

## 3. Trabajo adicional al alcance comprometido

Durante el sprint se agregó una mejora de seguridad sobre EP-01, gestionada como el cambio OpenSpec `add-mfa-sesiones` (ver [`openspec/changes/add-mfa-sesiones/`](../../../openspec/changes/add-mfa-sesiones/)):

- **Autenticación multifactor (MFA) con TOTP** como segundo factor del inicio de sesión.
- **Gestión segura de sesiones**: listar, revocar una o todas, renovación con detección de robo de sesión.

**Justificación.** RouteZero maneja datos personales de conductores y clientes protegidos por la Ley N° 29733, y los roles con mayor privilegio (Administrador, Gerente) no deberían depender de una sola contraseña. El detalle técnico está en [`02 Implementación del módulo de autenticación`](02%20Implementaci%C3%B3n%20del%20m%C3%B3dulo%20de%20autenticaci%C3%B3n%20V_1_0_0.md).

**Estado:** el backend está completo y verificado (30 de 39 tareas del cambio); faltan las pantallas del frontend, la cobertura de pruebas y el cierre documental.

## 4. Definition of Done — estado del módulo de autenticación

Criterios del DoD global ([`01 Transformando a ágil`](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md), sección 5):

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov y Jest | Pendiente (hay 44 comprobaciones de integración, ver documento 03; falta incorporarlas a `backend/tests/` y medir cobertura) |
| 2 | Análisis estático | 0 vulnerabilidades críticas (CodeQL o SonarQube) | Pendiente |
| 3 | Revisión de código | Pull Request aprobado antes del merge a `main` | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints documentados en Swagger/OpenAPI | Cumplido para los 9 endpoints de autenticación (`/docs`) |
| 6 | Criterios de aceptación verificados | Escenarios ejecutados y aprobados | Parcial (escenarios de `specs/mfa-totp` y `specs/session-management` verificados de extremo a extremo) |
| 7 | Cumplimiento de estándares | Sin errores W3C, Lighthouse ≥ 90, sin vulnerabilidades OWASP críticas | Parcial (ver mapeo OWASP en el documento 02); interfaz aún sin construir |
| 8 | Commit en rama e integración por Pull Request | Historia commiteada y integrada | Pendiente |

## 5. Plan de cierre del Sprint (26-09 → 02-10)

Propuesta de trabajo diario para llegar a la inspección con el sprint funcional. **Está sujeta a validación del equipo.**

| Día | Fecha | Foco | Resultado verificable |
|---|---|---|---|
| Sáb | 26-09 | Documentación de ejecución, commit de resguardo, tablas `vehiculos`, `clientes` y `pedidos`, autorización por rol | HU-002 completa en el backend |
| Dom | 27-09 | Backend de flota con validaciones y pruebas | HU-003, HU-004, HU-005 y HT-04 |
| Lun | 28-09 | Backend de pedidos con zona de cobertura, registro de auditoría y consentimiento | HU-006, HU-007, HU-008, HT-05, HT-01 y HT-02 |
| Mar | 29-09 | Frontend base: proyecto React, inicio de sesión, MFA y sesiones | HU-001 completa |
| Mié | 30-09 | Frontend de flota y pedidos, control de acceso por rol en la interfaz | HU-002, HU-003 a HU-008 de extremo a extremo |
| Jue | 01-10 | Despliegue en Render y Vercel, pruebas de aceptación, cobertura, Pull Request y etiqueta `v0.1.0` | HT-03, DoD |
| Vie | 02-10 | Inspección | Demostración del sprint |

**Orden de recorte si el tiempo no alcanza** (de lo primero que se sacrificaría a lo último): (1) despliegue en la nube (HT-03), que se reemplazaría por una demostración local documentada; (2) pantallas de MFA y sesiones, manteniendo el inicio de sesión; (3) HT-02. La gestión de flota y de pedidos, con el acceso por rol, se mantiene como núcleo del sprint.

## 6. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Plazo de una semana para 28 SP pendientes más el frontend | No cerrar el sprint completo | Plan diario de la sección 5 y orden de recorte |
| Primer contacto del equipo con React en este proyecto | Retrasos en las pantallas | Pantallas mínimas y reutilización de componentes; verificación manual diaria |
| Despliegue en Render y Vercel depende de cuentas y variables de entorno | HT-03 fuera del sprint | Demostración local como alternativa documentada |
| Cambios de diseño descubiertos al probar contra el proveedor de identidad | Retrabajo | Registro de cambios y pruebas de extremo a extremo antes de construir sobre cada pieza |

## 7. Evidencias

- Cambio OpenSpec `add-mfa-sesiones`: [`proposal.md`](../../../openspec/changes/add-mfa-sesiones/proposal.md), [`design.md`](../../../openspec/changes/add-mfa-sesiones/design.md), [`tasks.md`](../../../openspec/changes/add-mfa-sesiones/tasks.md).
- Código del backend: [`backend/`](../../../backend/).
- Plan y resultados de pruebas: [`03 Plan y resultados de pruebas`](03%20Plan%20y%20resultados%20de%20pruebas%20V_1_0_0.md).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-09-26 | Versión inicial: estado del Sprint 1 al 26-09-2026 y plan de cierre | Inciso Aguilar Elizabeth Antonela |
