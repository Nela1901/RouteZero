# 01 Sprint 1 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 1 — Base del sistema (19 sep – 02 oct 2026) |
| **Fecha de corte** | 2026-09-28 |
| **Inspección** | 2026-10-02 |
| **Versión** | 1.2.0 |

[← Volver al README Principal](../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)):

> *Implementar la base del sistema RouteZero: autenticación JWT con control de acceso por roles (EP-01), gestión de flota de vehículos (EP-02) y registro de pedidos con coordenadas GPS (EP-03).*

El sprint compromete **13 ítems y 42 Story Points** (8 Historias de Usuario y 5 Historias Técnicas). Este documento registra el estado real de cada ítem a la fecha de corte y el plan para cerrar el sprint antes de la inspección.

## 2. Alcance comprometido y estado al 28-09-2026

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem está implementada y verificada) y **Pendiente** (sin implementación).

| ID | Título | Épica | SP | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema | EP-01 | 3 | Completada | Backend completo (bloqueo RN-001) + frontend: pantalla de login, verificación MFA en dos pasos, redirección automática según el rol devuelto por `/api/auth/me` | — |
| HU-002 | Acceder solo a módulos permitidos por rol | EP-01 | 3 | Completada | Autorización por rol en la API (`requiere_rol`) + frontend: Administrador/Operador ven el panel completo (mapa, flota, pedidos, seguridad), Conductor recibe una vista propia mobile-first en vez del panel de escritorio | — |
| HU-003 | Registrar vehículo en la flota | EP-02 | 3 | Completada | Backend + pantalla "Flota" (listar, filtrar, registrar) conectada a la API real | — |
| HU-004 | Editar datos de un vehículo | EP-02 | 2 | Completada | Backend + edición de estado desde la pantalla de Flota | — |
| HU-005 | Consultar disponibilidad de la flota | EP-02 | 2 | Completada | `GET /api/vehiculos` con filtro por estado, reflejado en la interfaz | — |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | EP-03 | 3 | Completada | Backend + pantalla "Pedidos" (alta con selección de cliente, mapa real de Huancayo con Leaflet + OpenStreetMap mostrando los pedidos) | — |
| HU-007 | Registrar pedido con punto de referencia | EP-03 | 2 | Completada | Cubierta por diseño desde el backend; el frontend expone el campo como texto libre | — |
| HU-008 | Cancelar pedido pendiente | EP-03 | 2 | Completada | Backend + botón "Cancelar" en la pantalla de Pedidos (solo visible si el pedido sigue `PENDIENTE`) | — |
| HT-01 | Autenticación JWT y protección OWASP Top 10 | EP-01 | 8 | Parcial | JWT verificado con llave pública (ES256, `leeway`); autorización por rol; SQL parametrizado; CORS restrictivo; RLS; **87 % de cobertura con pytest-cov** sobre `src/auth/` y `src/core/security.py` (`backend/tests/test_sesiones.py`, `test_mfa.py`) | Registro de eventos en `logs_auditoria`, prueba explícita de inyección SQL, análisis estático (CodeQL o SonarQube) |
| HT-02 | Cifrado de datos y cumplimiento de la Ley N° 29733 | EP-01 | 5 | Pendiente | Ningún dato sensible de conductores se almacena todavía | Registro del consentimiento explícito (RN-013) y verificación del cifrado en reposo del proveedor |
| HT-03 | Infraestructura de despliegue en Render y Vercel | EP-01 | 5 | Pendiente | Base de datos ya alojada en Supabase | Despliegue del backend en Render y del frontend en Vercel |
| HT-04 | Pruebas unitarias del módulo de flota | EP-02 | 2 | Completada | `backend/tests/test_flota.py`: 10 pruebas con pytest, 93-100 % de cobertura sobre `src/flota/` | — |
| HT-05 | Pruebas unitarias del módulo de pedidos | EP-03 | 2 | Completada | `backend/tests/test_pedidos.py`: 15 pruebas con pytest, 90-100 % de cobertura sobre `src/clientes/` y `src/pedidos/` | — |

**Resumen del corte:** de los 42 SP comprometidos, **34 SP están completados** (HU-001 a HU-008, HT-04, HT-05), **8 SP tienen avance parcial** (HT-01) y 10 SP están pendientes (HT-02, HT-03).

## 3. Trabajo adicional al alcance comprometido

Durante el sprint se agregó una mejora de seguridad sobre EP-01, gestionada como el cambio OpenSpec `add-mfa-sesiones` (ver [`openspec/changes/add-mfa-sesiones/`](../../openspec/changes/add-mfa-sesiones/)):

- **Autenticación multifactor (MFA) con TOTP**, con pantalla propia de inscripción (código QR) además de la verificación en el login.
- **Gestión segura de sesiones**: listar, revocar una o todas (con confirmación), renovación con detección de robo de sesión — con pantalla propia en el frontend.

También se agregó un módulo mínimo `clientes/` (registrar y listar) como prerrequisito de `pedidos/`, no comprometido explícitamente en el sprint pero necesario para HU-006. El alcance completo de HU-010 (preferencias de entrega del cliente) queda para su propio sprint (EP-04).

**Justificación.** RouteZero maneja datos personales de conductores y clientes protegidos por la Ley N° 29733, y los roles con mayor privilegio (Administrador, Gerente) no deberían depender de una sola contraseña. El detalle técnico está en [`02 Implementación del módulo de autenticación`](02%20Implementaci%C3%B3n%20del%20m%C3%B3dulo%20de%20autenticaci%C3%B3n%20V_1_0_0.md).

**Estado del cambio `add-mfa-sesiones`:** grupos 1 a 7 de `tasks.md` completos (backend, frontend de MFA y sesiones); solo falta el grupo 8 (cierre: base de datos V_1_3_0, análisis estático, Pull Request).

**Frontend construido hoy (28-09), no detallado en el alcance original por historia:** proyecto React con Vite y TypeScript en `frontend/`, con tema oscuro/claro persistente, mapa real de Huancayo (Leaflet + tiles de OpenStreetMap, sin costo), panel de operaciones para Administrador/Operador y una vista mobile-first propia para Conductor.

## 4. Definition of Done — estado del proyecto

Criterios del DoD global ([`01 Transformando a ágil`](../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md), sección 5):

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov y Jest | Cumplido en el backend (92 % combinado: auth, flota, clientes, pedidos, `backend/tests/`); parcial en el frontend (Jest/Vitest solo cubre los componentes de MFA, faltan Flota y Pedidos) |
| 2 | Análisis estático | 0 vulnerabilidades críticas (CodeQL o SonarQube) | Pendiente |
| 3 | Revisión de código | Pull Request aprobado antes del merge a `main` | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints documentados en Swagger/OpenAPI | Cumplido para los 9 endpoints de autenticación, 3 de flota y 5 de pedidos/clientes (`/docs`) |
| 6 | Criterios de aceptación verificados | Escenarios ejecutados y aprobados | Cumplido de extremo a extremo (backend + frontend) para HU-001 a HU-008 y `specs/mfa-totp`/`specs/session-management` |
| 7 | Cumplimiento de estándares | Sin errores W3C, Lighthouse ≥ 90, sin vulnerabilidades OWASP críticas | Parcial (ver mapeo OWASP en el documento 02); Lighthouse y validación W3C del frontend todavía no corridos |
| 8 | Commit en rama e integración por Pull Request | Historia commiteada y integrada | Parcial (commiteado en `backend`, subido a `origin/backend`; Pull Request a `main` pendiente; rama `frontend` todavía sin crear/subir) |

## 5. Plan de cierre del Sprint (28-09 → 02-10)

El 28-09 se adelantó casi todo lo que estaba planificado para el 29-09 y el 01-10 juntos: frontend completo (login, MFA, sesiones, mapa, flota, pedidos) y toda la cobertura de pruebas del backend. Plan actualizado para los días restantes. **Está sujeta a validación del equipo.**

| Día | Fecha | Foco | Resultado verificable |
|---|---|---|---|
| ~~Dom~~ | ~~27-09~~ | ~~Backend de flota y de pedidos~~ | **Cumplido:** HU-003 a HU-008 |
| ~~Lun~~ | ~~28-09~~ | ~~Frontend completo, MFA/sesiones en la interfaz, cobertura pytest de todo el backend~~ | **Cumplido:** HU-001, HU-002, HT-04, HT-05; 92 % de cobertura backend |
| Mar | 29-09 | Registro de auditoría (`logs_auditoria`), prueba explícita de inyección SQL, análisis estático (CodeQL o SonarQube) | HT-01 completa |
| Mié | 30-09 | Consentimiento explícito (RN-013) y cifrado en reposo (HT-02); pruebas Jest de Flota y Pedidos en el frontend | HT-02 completa, DoD #1 completo |
| Jue | 01-10 | Nueva versión de la base de datos (V_1_3_0, con flota/clientes/pedidos), Pull Request de `backend` a `main`, rama `frontend`, despliegue en Render/Vercel si alcanza el tiempo | HT-03 (si alcanza), DoD |
| Vie | 02-10 | Inspección | Demostración del sprint |

**Orden de recorte si el tiempo no alcanza** (de lo primero que se sacrificaría a lo último): (1) despliegue en la nube (HT-03), reemplazado por una demostración local documentada; (2) análisis estático automatizado (revisión manual como alternativa); (3) HT-02. El núcleo funcional del sprint (backend, frontend y sus pruebas) ya está asegurado.

## 6. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| El Custom Access Token Hook de Supabase parece cachear el `token_version` del usuario: tras revocar sesiones, un login nuevo puede seguir recibiendo un valor viejo y fallar con "Token revocado" | Un usuario real que cierre todas sus sesiones podría quedar bloqueado hasta reintentar | Revisar en el panel de Supabase si el hook tiene caché de resultado activada y desactivarla; documentar el hallazgo en `design.md` junto a las otras rarezas de Supabase ya registradas |
| Pocos días restantes concentrados en cierre documental y no funcional (auditoría, análisis estático, despliegue) | No cerrar el sprint al 100 % del DoD | Plan diario de la sección 5 y orden de recorte |
| Despliegue en Render y Vercel depende de cuentas y variables de entorno | HT-03 fuera del sprint | Demostración local como alternativa documentada |

## 7. Evidencias

- Cambio OpenSpec `add-mfa-sesiones`: [`proposal.md`](../../openspec/changes/add-mfa-sesiones/proposal.md), [`design.md`](../../openspec/changes/add-mfa-sesiones/design.md), [`tasks.md`](../../openspec/changes/add-mfa-sesiones/tasks.md).
- Código del backend: [`backend/`](../../backend/), módulos `auth/`, `flota/`, `clientes/` y `pedidos/`; suite de pruebas en `backend/tests/`.
- Código del frontend: [`frontend/`](../../frontend/) (React + Vite + TypeScript).
- Scripts de verificación manual de extremo a extremo (histórico, previos a la suite de pytest): `backend/tests_manual/`.
- Plan y resultados de pruebas: [`03 Plan y resultados de pruebas`](03%20Plan%20y%20resultados%20de%20pruebas%20V_1_0_0.md).

[← Volver al README Principal](../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-09-26 | Versión inicial: estado del Sprint 1 al 26-09-2026 y plan de cierre | Inciso Aguilar Elizabeth Antonela |
| V_1_1_0 | 2026-09-27 | Estado al 27-09-2026: HU-003 a HU-008 completadas, autorización por rol (HU-002) implementada en la API, ajuste del plan de cierre | Inciso Aguilar Elizabeth Antonela |
| V_1_2_0 | 2026-09-28 | Estado al 28-09-2026: frontend completo (login, MFA, sesiones, mapa, flota, pedidos), HU-001/HU-002 completadas, 92 % de cobertura de pruebas en el backend (HT-04/HT-05 completadas), ajuste del plan de cierre | Inciso Aguilar Elizabeth Antonela |
