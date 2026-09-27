# Proposal

## Why

RouteZero maneja datos operativos sensibles de Andina Reparto S.A.C. (flota, pedidos, conductores, clientes) protegidos por la Ley N° 29733, pero la autenticación actual (HU-001, HT-01) solo exige correo y contraseña, con bloqueo tras 3 intentos fallidos. Un solo factor es insuficiente para roles con alto privilegio (Administrador, Gerente) y no hay mecanismo de revocación de sesiones activas, lo que deja una ventana de exposición si una contraseña o un token de acceso se ve comprometido. Se necesita un segundo factor (TOTP) y una gestión de sesiones que permita revocar y auditar accesos, antes de que el módulo de autenticación pase a producción. En vez de construir contraseña, JWT y MFA completamente desde cero, se aprovecha Supabase Auth (ya elegido como proveedor de hosting de la base de datos, `10. Stack tecnológico V_1_1_0`) como proveedor de identidad, reservando el desarrollo propio para las reglas de negocio específicas de RouteZero que Supabase no cubre.

## What Changes

- Se agrega inscripción y verificación de MFA por TOTP, usando el mecanismo nativo de Supabase Auth (`auth.mfa`), orquestado siempre a través de nuestro backend — el frontend nunca llama a Supabase directamente, para preservar la arquitectura de tres capas ya documentada.
- El login pasa a dos pasos cuando el usuario tiene MFA activo: credenciales válidas → solicitud de código TOTP de 6 dígitos → el backend completa el desafío MFA con Supabase y solo entonces entrega tokens al cliente.
- La autenticación (contraseña, emisión y firma de JWT, rotación de refresh token) se delega a Supabase Auth (`auth.users`). Nuestro backend valida los tokens emitidos por Supabase y añade dos reglas de negocio que Supabase no ofrece con la precisión requerida: el bloqueo exacto de RN-001 (3 intentos, 15 minutos) y un bloqueo independiente para intentos fallidos de código TOTP.
- La tabla `usuarios` pasa a ser un perfil de aplicación referenciado a `auth.users(id)` de Supabase, en vez de almacenar su propio hash de contraseña.
- Se agrega gestión de sesiones activas propia: el usuario puede listar sus sesiones (dispositivo, IP, fechas) y cerrar sesiones individuales o todas remotamente, respaldada por una tabla propia `sesiones_activas` que refleja el estado real de las sesiones de Supabase.
- **BREAKING**: el contrato de la respuesta de login cambia — ya no retorna un token único; retorna `access_token` + `refresh_token` (emitidos por Supabase), o un estado intermedio `mfa_required` cuando el usuario tiene TOTP activo.
- Se añade Row Level Security (RLS) en PostgreSQL sobre `usuarios` y `sesiones_activas`, de modo que un usuario solo pueda leer sus propios registros a nivel de base de datos, no solo a nivel de aplicación.
- Se restringe la configuración CORS del backend FastAPI al origen exacto del frontend desplegado.
- Se documentan en `.env.example` las nuevas variables de entorno requeridas (credenciales de Supabase para el backend, nunca expuestas al frontend).

## Capabilities

### New Capabilities
- `mfa-totp`: inscripción, verificación y desactivación de autenticación multifactor basada en TOTP (RFC 6238), orquestada a través del backend sobre Supabase Auth, como segundo factor del login.
- `session-management`: emisión de tokens de acceso/refresco vía Supabase Auth, listado y revocación de sesiones activas por usuario a través de una tabla propia sincronizada con el estado real de Supabase.

### Modified Capabilities
(Ninguna: no existen capabilities previas en `openspec/specs/` — HU-001/HT-01 nunca se formalizaron como spec de OpenSpec, por lo que el login de un solo factor queda absorbido como parte del flujo descrito en `session-management` en vez de modificarse como delta.)

## Impact

- **Backend (FastAPI)**: nuevo router de autenticación extendido (`/api/auth/mfa/*`, `/api/auth/sesiones/*`) que actúa como intermediario hacia Supabase Auth usando solo su clave pública (`anon key`), nuevos servicios (`ServicioMFA`, `ServicioSesiones`) y repositorios (`RepositorioUsuarios`, `RepositorioSesiones`), siguiendo el patrón Repository ya establecido. El frontend **nunca** llama a Supabase directamente.
- **Base de datos (Supabase PostgreSQL)**: `usuarios` pasa a referenciar `auth.users(id)`; nueva tabla `sesiones_activas`; políticas RLS asociadas; columnas de bloqueo propio en `usuarios` (contraseña y MFA, contadores independientes). Ya no se necesita una tabla `mfa_secrets` propia — el secreto TOTP lo administra Supabase internamente.
- **Frontend (React)**: nueva pantalla de enrolamiento TOTP (QR), nueva pantalla de verificación de código, y ajuste del flujo de login para manejar el estado intermedio `mfa_required` — siempre contra nuestra propia API, nunca contra Supabase directamente.
- **Configuración**: nuevas variables en `.env` / `.env.example` (credenciales de Supabase); configuración de CORS restrictiva en FastAPI; ajuste de la duración del token de acceso (15 min) en el panel de Supabase.
- **Documentación del proyecto**: requiere actualizar `docs/01 Inicio/11. Base de datos` a una nueva versión (la FK de `usuarios` cambia de autocontenida a dependiente de `auth.users`).
- **Compatibilidad**: cambio de contrato en el endpoint de login (ver BREAKING arriba) — cualquier cliente actual del endpoint de login deberá actualizarse para manejar el nuevo flujo de dos pasos y el par access/refresh token emitido por Supabase.
