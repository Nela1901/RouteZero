# 03 Plan y Resultados de Pruebas

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha de corte** | 2026-09-26 |
| **Alcance** | Módulo de autenticación (cambio OpenSpec `add-mfa-sesiones`) |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Estrategia de pruebas

Las pruebas del módulo de autenticación son de **integración de extremo a extremo**: se ejecutan contra el servidor FastAPI local y contra el proyecto real de Supabase (identidad y base de datos), sin simulaciones. Se eligió este enfoque porque las decisiones de seguridad más delicadas (rotación de tokens, RLS, MFA) dependen del comportamiento real del proveedor, y varias de ellas se corrigieron precisamente al probarlas así (sección 5).

| Nivel | Estado |
|---|---|
| Integración de extremo a extremo (API + Supabase real) | Realizado: 44 comprobaciones automatizadas (CP-01 a CP-44) y 12 verificaciones puntuales (CP-45 a CP-56) |
| Pruebas unitarias con medición de cobertura (pytest-cov, DoD ≥ 80 %) | Pendiente |
| Pruebas de aceptación con la interfaz | Pendiente (el frontend aún no existe) |
| Pruebas de rendimiento | No aplica al módulo de autenticación; corresponde al motor de optimización (RNF-001) |
| Análisis estático de seguridad (CodeQL o SonarQube) | Pendiente |

**Entorno:** Windows 11, Python 3.13, FastAPI en `127.0.0.1:8000`, Supabase (región São Paulo) con PostgreSQL 15+, conexión con el rol `app_backend` (sin `BYPASSRLS`). Cuenta de prueba dedicada. Expiración del token de acceso: 900 s.

## 2. Casos de prueba de autenticación y sesiones

Automatizados en un script de extremo a extremo. Trazabilidad: HU-001, RN-001, HT-01 y los escenarios de [`specs/mfa-totp`](../../../openspec/changes/add-mfa-sesiones/specs/mfa-totp/spec.md) y [`specs/session-management`](../../../openspec/changes/add-mfa-sesiones/specs/session-management/spec.md).

| ID | Caso | Resultado esperado | Resultado |
|---|---|---|---|
| CP-01 | Iniciar sesión sin MFA | 200 con access y refresh token | Aprobado |
| CP-02 | Llamar a un endpoint protegido con ese token | 200 | Aprobado |
| CP-03 | Listar sesiones tras iniciar sesión | 1 sesión, marcada como actual, con el dispositivo | Aprobado |
| CP-04 | Renovar tokens | 200 con tokens nuevos | Aprobado |
| CP-05 | Usar el token renovado | 200 | Aprobado |
| CP-06 | Listar sesiones tras renovar | Sigue siendo 1 sesión | Aprobado |
| CP-07 | Reusar el refresh token anterior dentro de 10 s | 200, sin penalizar (reintento legítimo) | Aprobado |
| CP-08 | Renovar con un refresh token inventado | 401 | Aprobado |
| CP-09 | Usar la sesión tras el intento con token inventado | 200 (la sesión no se afecta) | Aprobado |
| CP-10 | Reusar el refresh token anterior pasados 10 s | 401 (robo de sesión) | Aprobado |
| CP-11 | Usar el access token vigente tras detectar el robo | 401 (revocado) | Aprobado |
| CP-12 | Verificar `token_version` tras el robo | Incrementado en 1 | Aprobado |
| CP-13 | Tres contraseñas incorrectas seguidas | 401 las tres veces | Aprobado |
| CP-14 | Cuarto intento con la contraseña correcta | 429 con tiempo restante de bloqueo | Aprobado |
| CP-15 | Iniciar sesión con un correo inexistente | 401 con el mismo mensaje genérico | Aprobado |
| CP-16 | Listar sesiones con dos dispositivos | 2 sesiones, una marcada como actual | Aprobado |
| CP-17 | Revocar la sesión de otro dispositivo | 204 | Aprobado |
| CP-18 | Usar el token de la sesión revocada | 401 al instante | Aprobado |
| CP-19 | Listar sesiones tras revocar | Queda 1 sesión | Aprobado |
| CP-20 | Revocar una sesión inexistente o ajena | 404 | Aprobado |
| CP-21 | Cerrar la sesión propia | 204 | Aprobado |
| CP-22 | Usar el token de la sesión cerrada | 401 | Aprobado |
| CP-23 | Cerrar todas las sesiones | 204 | Aprobado |
| CP-24 | Usar cualquier token anterior | 401 en todos | Aprobado |
| CP-25 | Verificar `token_version` tras cerrar todas | Incrementado en 1 | Aprobado |
| CP-26 | Inscribir MFA | 200 con QR, secreto e identificador de factor | Aprobado |
| CP-27 | Confirmar la inscripción con un código TOTP válido | 204 | Aprobado |
| CP-28 | Verificar `mfa_activo` en la base | Verdadero | Aprobado |
| CP-29 | Usar una sesión de nivel bajo (aal1) creada antes del MFA | 401 (se exige la verificación MFA) | Aprobado |
| CP-30 | Iniciar sesión con MFA activo | 200 con `mfa_required`, sin refresh token | Aprobado |
| CP-31 | Usar el token parcial en la API | 401 | Aprobado |
| CP-32 | Verificar con un código incorrecto | 400 | Aprobado |
| CP-33 | Verificar con el código correcto | 200 con tokens de sesión completa | Aprobado |
| CP-34 | Usar la sesión completa (aal2) | 200 | Aprobado |
| CP-35 | Listar sesiones tras el login con MFA | Aparece la sesión con su dispositivo | Aprobado |
| CP-36 | Desactivar MFA con contraseña y código vigentes | 204 | Aprobado |
| CP-37 | Verificar `mfa_activo` tras desactivar | Falso | Aprobado |

## 3. Casos de prueba del mantenimiento de sesiones

| ID | Caso | Resultado esperado | Resultado |
|---|---|---|---|
| CP-38 | Sesión activa sin renovar hace 8 días | Pasa a `EXPIRADA` | Aprobado |
| CP-39 | Sesión revocada hace 31 días | Se borra | Aprobado |
| CP-40 | Sesión expirada hace 5 días | Se conserva | Aprobado |
| CP-41 | Sesión activa reciente | No se modifica | Aprobado |
| CP-42 | Sesión revocada reciente | Se conserva | Aprobado |
| CP-43 | Renovar una sesión inactiva más de 7 días | 401 por inactividad | Aprobado |
| CP-44 | Estado de esa sesión tras el intento | `EXPIRADA` | Aprobado |

## 4. Verificaciones puntuales

| ID | Verificación | Resultado |
|---|---|---|
| CP-45 | Bloqueo MFA: tres códigos TOTP inválidos seguidos, cuarto intento | 429 con bloqueo, independiente del bloqueo por contraseña. Aprobado |
| CP-46 | RLS: consulta con el rol de la aplicación sin usuario fijado | 0 filas. Aprobado |
| CP-47 | RLS: usuario fijado distinto del dueño de la fila | 0 filas. Aprobado |
| CP-48 | RLS: usuario fijado igual al dueño | 1 fila. Aprobado |
| CP-49 | Atributos de los roles de base de datos | `app_backend` sin `BYPASSRLS`, `app_admin` con `BYPASSRLS`. Aprobado |
| CP-50 | Reversión del esquema y nueva aplicación | Esquema idéntico y funcional. Aprobado |
| CP-51 | El token de acceso incluye el reclamo `ver` | Presente con valor 1. Aprobado |
| CP-52 | CORS con el origen del frontend | Cabecera de permiso presente. Aprobado |
| CP-53 | CORS con un origen ajeno | 400 sin cabecera de permiso. Aprobado |
| CP-54 | Los 6 endpoints protegidos y `/me` sin token y con token falso | 401 en los 14 casos. Aprobado |
| CP-55 | Duración del token de acceso | 900 s. Aprobado |
| CP-56 | Documentación Swagger | `/docs` responde 200 y lista los endpoints. Aprobado |

## 5. Defectos encontrados y corregidos

Las pruebas contra el proveedor real descubrieron problemas que el diseño en papel no anticipaba. Todos se corrigieron y se verificaron con los casos anteriores.

| ID | Defecto | Causa | Corrección |
|---|---|---|---|
| D-01 | La política RLS lanzaba un error en lugar de devolver 0 filas cuando no había usuario fijado | `current_setting` exige que la variable exista | Se usa `current_setting(..., true)` para que la política falle cerrado sin error |
| D-02 | El backend rechazaba todos los tokens válidos | Se verificaban con un secreto compartido (HS256) y el proyecto firma con llaves asimétricas (ES256) | Verificación con la llave pública (JWKS) y la dependencia `cryptography` |
| D-03 | La activación del MFA no se guardaba y no daba error | Cada método hacía su propio `commit`, cerrando la transacción donde vivía el usuario de RLS; la actualización siguiente corría sin RLS y no afectaba ninguna fila | Un único `commit` al final de la petición |
| D-04 | El contador de intentos fallidos nunca llegaba a 3 | Una respuesta de error esperada (código inválido) provocaba la reversión de toda la transacción, incluido el contador | Las respuestas de negocio esperadas conservan los cambios; solo los fallos inesperados revierten |
| D-05 | El inicio de sesión devolvía 500 al activar el hook del token | El rol interno de Supabase no tenía permiso para leer `usuarios` ni ejecutar la función | Permisos explícitos (`SELECT` y `EXECUTE`) |
| D-06 | Un refresh token ya rotado se aceptaba siempre | Supabase no detectó el reuso, ni siquiera con su ajuste activado y guardado | Detección propia con hashes del token vigente y del anterior, y ventana de gracia |
| D-07 | La revocación de la sesión de otro dispositivo fallaba (502) | El endpoint administrativo previsto no existe | La tabla `sesiones_activas` es autoritativa para la API; se eliminó la clave `service_role` |

## 6. Pruebas pendientes

| Prueba | Motivo | Cuándo |
|---|---|---|
| Cobertura con pytest-cov (≥ 80 %) | Incorporar las comprobaciones a `backend/tests/` y medir | Antes de cerrar el Sprint 1 |
| Inyección SQL explícita sobre el inicio de sesión (HT-01) | Falta el caso con cargas maliciosas y el registro de auditoría | Sprint 1 |
| Pruebas unitarias de flota y pedidos (HT-04, HT-05) | Los módulos aún no existen | Sprint 1 |
| Pruebas de aceptación, accesibilidad (Lighthouse ≥ 90) y W3C | El frontend aún no existe | Sprint 1 |
| Análisis estático (CodeQL o SonarQube) | Pendiente de configuración | Sprint 1 |

## 7. Reproducción

Las comprobaciones se ejecutaron con scripts de extremo a extremo (uno para autenticación y sesiones, otro para el mantenimiento) y con consultas directas a la base de datos. Su incorporación a `backend/tests/` con `pytest` está registrada en la tarea 6.3 del cambio OpenSpec, con las credenciales de la cuenta de prueba tomadas del archivo `.env` (nunca del repositorio).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-09-26 | Versión inicial: casos, resultados y defectos del módulo de autenticación | Inciso Aguilar Elizabeth Antonela |
