# Design

## Context

El backend aún no existe como código (RouteZero está en fase de planificación); este diseño se escribe contra la arquitectura decidida en `docs/01 Inicio/10. Stack tecnológico V_1_1_0` y `docs/01 Inicio/12. Modelo C4 V_1_1_0`: FastAPI con organización por características y patrón Repository, PostgreSQL 15+ alojado en Supabase, y un frontend React que consume la API **solo** por REST/JSON contra nuestro propio backend. Esta versión del diseño incorpora una decisión adicional del equipo: usar **Supabase Auth** como proveedor de identidad (contraseña, emisión de JWT, MFA por TOTP nativo) en vez de construir esas piezas desde cero, dado que el equipo ya tiene experiencia previa con Supabase y su base de datos ya vive ahí. Ver proposal.md - Why para la motivación completa.

## Goals / Non-Goals

**Goals:**
- Definir cómo el backend orquesta Supabase Auth sin exponer el frontend directamente a Supabase, preservando la arquitectura de tres capas ya documentada.
- Definir las reglas de negocio propias de RouteZero que Supabase Auth no cubre con la precisión requerida (bloqueo exacto de RN-001, bloqueo independiente de MFA, revocación inmediata de tokens de acceso).
- Definir el modelo de datos para `usuarios` (ahora dependiente de `auth.users`) y `sesiones_activas`.
- Fijar las decisiones de seguridad transversales (RLS, CORS, manejo de secretos, validación de entrada) como parte del diseño, no como detalles a decidir durante la implementación.

**Non-Goals:**
- No se diseña autenticación por factores distintos a TOTP (SMS, WebAuthn, etc.).
- No se diseña un panel de administración para forzar MFA a otros usuarios.
- No se migra el resto del sistema (flota, pedidos, rutas) a usar la API de Supabase directamente — esos módulos siguen usando SQLAlchemy contra Postgres, igual que antes; solo la identidad se delega a Supabase.

## Decisions

### 1. Supabase Auth como proveedor de identidad, siempre detrás de nuestro backend
El backend actúa como intermediario exclusivo: recibe las peticiones del frontend (login, inscripción MFA, verificación MFA, renovar, cerrar sesión) y, por detrás, llama a la API de Supabase Auth. El frontend nunca establece una conexión directa con Supabase.

El backend usa únicamente la **clave pública** (`anon key`), reenviando el propio token de acceso del usuario cuando corresponde — el mismo patrón que usaría un cliente móvil o web hablando directo con Supabase, solo que aquí pasa por nuestra API en el medio. Esto cubre: login, inscripción/verificación de MFA propio, renovar el propio token y cerrar la propia sesión.

**No se usa la clave `service_role`** (privilegios administrativos): se había previsto para revocar una sesión de otro dispositivo, pero al implementarlo se comprobó que Supabase no ofrece un endpoint para invalidar una sesión concreta ajena (`DELETE /auth/v1/admin/sessions/{id}` responde 404), y no hace falta: nuestra tabla `sesiones_activas` es autoritativa para nuestra API (ver Decisión 5). Evitar guardar un secreto con privilegios totales sobre el proyecto es además una mejora de seguridad.

```
Frontend (React) → nuestra API (FastAPI) → Supabase Auth API (anon key + token del usuario)
                                          → PostgreSQL (SQLAlchemy, con RLS)
```

**Alternativa considerada**: dejar que el frontend use `supabase-js` directamente contra Supabase Auth (patrón común en apps que usan Supabase de punta a punta). Se descartó porque contradice la arquitectura de tres capas ya evaluada y justificada en `10. Stack tecnológico`, y porque dificultaría aplicar nuestras reglas de bloqueo propias (RN-001, bloqueo MFA independiente) de forma centralizada.

**Alternativa considerada**: construir contraseña, JWT y TOTP completamente desde cero (diseño original de este cambio, ver historial de versiones). Se descartó tras confirmar que el equipo ya tiene experiencia productiva con Supabase Auth + roles propios en otro proyecto, reduciendo el riesgo de adoptar este patrón.

### 2. `usuarios` como tabla de perfil dependiente de `auth.users`
Ya no almacenamos contraseña ni gestionamos su hash — eso lo hace Supabase en su esquema interno `auth`. Nuestra tabla de perfil vive en el esquema `public` de la misma base de datos de Supabase:

```sql
ALTER TABLE usuarios
    DROP COLUMN password_hash,
    ADD COLUMN usuario_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    ADD COLUMN mfa_activo BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN mfa_intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN mfa_bloqueado_hasta TIMESTAMP WITH TIME ZONE,
    ADD COLUMN token_version INTEGER NOT NULL DEFAULT 1;
```

(`intentos_fallidos` y `bloqueado_hasta` para el bloqueo por contraseña, RN-001, ya existían en el esquema original de `docs/11. Base de datos`; se conservan sin cambios.)

Los contadores de bloqueo de contraseña (`intentos_fallidos`/`bloqueado_hasta`) y de MFA (`mfa_intentos_fallidos`/`mfa_bloqueado_hasta`) son **independientes entre sí**: agotar los 3 intentos de un factor no bloquea ni comparte estado con el otro. Ambos los aplica nuestro backend como una capa sobre el login/verificación de Supabase, porque Supabase Auth no ofrece "bloquear esta cuenta exactamente 15 minutos tras 3 fallos" como regla configurable — solo rate limiting genérico por IP.

**Alternativa considerada**: dejar que Supabase gestione también el bloqueo por intentos fallidos con su rate limiting nativo. Se descartó porque no reproduce la regla de negocio exacta ya documentada (RN-001: 3 intentos, 15 minutos, por cuenta), que es una regla ya aprobada en una entrega previa del curso y no se puede relajar sin volver a esa fase.

### 3. Ya no existe una tabla `mfa_secrets` propia
El secreto TOTP y su estado de verificación los administra Supabase internamente (`auth.mfa_factors`, `auth.mfa_challenges`). Nuestro backend solo orquesta las llamadas de enrolamiento/desafío/verificación a través de la API de administración de Supabase, y aplica el contador de bloqueo independiente (`mfa_intentos_fallidos`) sobre esas llamadas.

### 4. Tolerancia de reloj para la validación de códigos TOTP
Se configura la verificación de TOTP de Supabase con la tolerancia estándar de ±1 paso de tiempo (ventana total de 90 segundos), para absorber desfases de reloj razonables sin ampliar significativamente la superficie de fuerza bruta. Esta es una configuración del proveedor, no código propio.

### 5. `sesiones_activas`: tabla propia como espejo visible de las sesiones de Supabase
Supabase Auth emite y rota los tokens, pero **no se puede confiar en él para detectar el reuso de refresh tokens**: se comprobó empíricamente que este proyecto acepta refresh tokens ya rotados (incluso el "abuelo", R1 tras R1→R2→R3, e incluso pasada la ventana de reuso de 10 s) devolviendo la sesión activa, con "Detect and revoke potentially compromised refresh tokens" activado y guardado en el panel. Por eso esa detección la implementa nuestro backend (ver abajo), y nuestra tabla `sesiones_activas` cumple dos funciones: metadatos para que el usuario vea y administre sus sesiones, y estado autoritativo de cada sesión para nuestra API:

```sql
CREATE TABLE sesiones_activas (
    sesion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    supabase_session_id TEXT NOT NULL UNIQUE,
    dispositivo_info TEXT,
    ip_origen VARCHAR(45),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ultimo_uso_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVA'
        CHECK (estado IN ('ACTIVA', 'REVOCADA', 'EXPIRADA')),
    refresh_token_hash TEXT,
    refresh_token_anterior_hash TEXT,
    rotada_en TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sesiones_usuario ON sesiones_activas(usuario_id);
CREATE INDEX idx_sesiones_estado ON sesiones_activas(estado);
```

- Al completar un login, el backend crea una fila aquí junto con la sesión real de Supabase (`supabase_session_id` guarda el identificador de sesión que devuelve Supabase).
- **Nuestra tabla es autoritativa para nuestra API** (corrección tras implementar): `get_current_user` exige que el `session_id` del token esté registrado y `ACTIVA` en esta tabla, y `renovar` se niega a renovar sesiones que no lo estén. Consecuencias: (a) revocar una sesión ajena basta con marcarla `REVOCADA` — sus tokens dejan de servir de inmediato, sin esperar los 15 min y sin necesitar `service_role`; (b) un token obtenido llamando a Supabase directamente (la `anon key` es pública), sin pasar por nuestro login, no sirve contra nuestra API porque su sesión no está registrada.
- Al cerrar la **sesión actual**, el backend además llama a `logout?scope=local` de Supabase; al cerrar **todas**, a `scope=global`, marca todas las filas `REVOCADA` e incrementa `token_version`.
- **Rotación y detección de reuso propias** (`renovar`): la fila guarda el hash SHA-256 (nunca el token) del refresh token vigente y del anterior, y cuándo se rotó (`rotada_en`). Al renovar, la fila se lee con `SELECT ... FOR UPDATE`, de modo que dos renovaciones simultáneas de la misma sesión se serializan y la segunda ya ve el token rotado por la primera (sin carreras). Según el token presentado:
  - **el vigente** → renovación normal; se guardan los hashes nuevos (el vigente pasa a anterior);
  - **el anterior, dentro de 10 s** de la rotación → reintento legítimo (dos pestañas, red lenta): no se penaliza y se le devuelve la sesión vigente;
  - **el anterior, pasados los 10 s** → robo: alguien conserva un token que el dueño ya rotó. Se marca la sesión `REVOCADA` y se incrementa `token_version` (los access tokens vigentes dejan de servir);
  - **cualquier otro** (basura, o un token muy antiguo) → 401 sin efectos sobre la sesión, para que enviar tokens inventados no permita cerrar la sesión de otra persona.
- Una sesión que vence en Supabase sin más actividad puede seguir apareciendo como `ACTIVA` en el listado hasta que el job de sincronización la marque (ver Riesgos); es una inconsistencia de **presentación**, no de seguridad, porque sin refresh válido no hay forma de obtener tokens nuevos y el access token vence a los 15 min.
- Se agrega una tarea de limpieza periódica que borra filas en estado `REVOCADA`/`EXPIRADA` con más de 30 días de antigüedad, para que la tabla no crezca indefinidamente (alineado con Green Software, HT-11).

**Alternativa considerada**: no tener tabla propia y depender 100% de la API de Supabase para listar sesiones. Se descartó porque el listado de sesiones para el propio usuario final (con dispositivo/IP) no está garantizado como una función de cliente de primera clase en todos los planes de Supabase; una tabla propia nos da control total sobre qué se muestra.

### 6. Revocación inmediata de tokens de acceso mediante un reclamo de versión propio
Aunque Supabase invalida el **refresh token** de inmediato al cerrar sesión, el **access token** ya emitido (JWT) sigue siendo válido hasta su expiración natural (configurada a 15 minutos), igual que ocurriría con cualquier JWT firmado. Para eliminar esa ventana de exposición en los casos que importan, se usa el **Custom Access Token Hook** de Supabase (una función de Postgres que Supabase ejecuta antes de firmar cada token) para embeber un reclamo `ver` con el valor de `usuarios.token_version`:

```sql
CREATE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    claims jsonb;
    version INTEGER;
BEGIN
    SELECT token_version INTO version FROM public.usuarios WHERE usuario_id = (event->>'user_id')::UUID;
    claims := event->'claims';
    claims := jsonb_set(claims, '{ver}', to_jsonb(COALESCE(version, 1)));
    event := jsonb_set(event, '{claims}', claims);
    RETURN event;
END;
$$;
```

El middleware de nuestro backend, al validar cada token de acceso, compara el reclamo `ver` contra `usuarios.token_version` actual (aprovechando la misma consulta que ya necesita para cargar el rol del usuario) y rechaza el token si no coincide. `token_version` se incrementa solo en dos eventos infrecuentes: detección de reutilización de refresh token, o "cerrar todas las sesiones" explícito.

**Alternativa considerada**: aceptar la ventana de hasta 15 minutos como riesgo residual sin mitigar. Se descartó porque ya se había identificado como hallazgo de auditoría en una iteración anterior de este mismo diseño, y el hook de Supabase permite resolverlo sin renunciar a los beneficios de delegar la autenticación.

### 7. Row Level Security (RLS) sobre `usuarios` y `sesiones_activas`
Se mantiene RLS sobre ambas tablas, con el mismo patrón ya usado: el backend fija `app.usuario_actual_id` en la conexión/transacción a partir del `usuario_id` extraído del token de acceso ya validado (no usamos `auth.uid()` de Supabase porque nuestro backend se conecta directamente con SQLAlchemy, no a través de la capa PostgREST de Supabase, así que esa función no se resuelve automáticamente en nuestras consultas).

```sql
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE sesiones_activas ENABLE ROW LEVEL SECURITY;

CREATE POLICY usuarios_solo_propio ON usuarios
    USING (usuario_id = NULLIF(current_setting('app.usuario_actual_id', true), '')::UUID);

CREATE POLICY sesiones_solo_propias ON sesiones_activas
    USING (usuario_id = NULLIF(current_setting('app.usuario_actual_id', true), '')::UUID);
```

(Se usa `current_setting(..., true)` para que, si la variable no está fijada, la política devuelva 0 filas en vez de lanzar un error; el resultado sigue siendo *fail-closed*.)

**Corrección tras implementar**: la referencia de `sesiones_activas` a `usuarios` no tenía `ON DELETE CASCADE`. Al intentar borrar un usuario de prueba desde el panel de Supabase, la eliminación en cadena hacia `usuarios` (que sí tiene `ON DELETE CASCADE` desde `auth.users`) quedaba bloqueada por las filas de `sesiones_activas` que aún referenciaban a ese usuario, con el error genérico "Database error deleting user". Se agregó `ON DELETE CASCADE` a esa clave foránea.

Al crear el proyecto de Supabase, se activó "Enable automatic RLS" para que cualquier tabla nueva del esquema `public` nazca protegida por defecto (comportamiento *fail-closed*). El backend se conecta con un rol propio, `app_backend`, **sin** `BYPASSRLS` (el usuario `postgres` que Supabase entrega por defecto sí lo tiene y se saltaría todas las políticas); un rol administrativo separado, `app_admin`, lo tiene para tareas de mantenimiento (limpieza de sesiones viejas).

**Corrección tras implementar (grupo 5 / autorización por rol)**: ese mismo ajuste automático activó RLS también en `roles`, una tabla de referencia sin dato sensible por usuario, y sin ninguna política asociada — el efecto fue que `app_backend` no podía leer ninguna fila de `roles` (0 filas, sin error), bloqueando en silencio cualquier consulta que necesitara el nombre del rol del usuario (por ejemplo, para la autorización). Se agregó una política de solo lectura sin restricción: `CREATE POLICY roles_lectura_app ON roles FOR SELECT USING (true)`. Cualquier tabla de catálogo/referencia nueva (sin dato por usuario) que se cree en el futuro debe recibir una política equivalente, o quedará inaccesible por el mismo motivo.

Como `app_backend` no puede leer el esquema `auth`, el login localiza la cuenta por correo mediante una función `public.usuario_id_por_email(text)` con `SECURITY DEFINER`, ejecutable solo por ese rol. Con ese `usuario_id`, el backend fija `app.usuario_actual_id` antes de aplicar el bloqueo de RN-001: actúa de confianza sobre la cuenta que se está autenticando, todavía sin token.

### 8. CORS restrictivo por configuración
El middleware CORS de FastAPI se configura con un origen exacto leído de variable de entorno (`FRONTEND_ORIGIN`), nunca con `allow_origins=["*"]`.

### 9. Variables de entorno nuevas
Se añaden a `.env.example` (sin valores reales, ya que `.env` está en `.gitignore`):

```
DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
FRONTEND_ORIGIN=
```

`SUPABASE_ANON_KEY` es pública y cubre todas las operaciones de Auth (login, MFA propio, renovar, cerrar la propia sesión), reenviando el token del usuario cuando corresponde. No hay ninguna clave administrativa: `SUPABASE_SERVICE_ROLE_KEY` se descartó (ver Decisión 1).

**Corrección tras implementar (grupo 3)**: originalmente se planeó `SUPABASE_JWT_SECRET` para verificar la firma localmente (HS256). En la práctica, el proyecto de Supabase ya usa **llaves asimétricas (ES256)**, no el secreto compartido legacy. La verificación real usa el endpoint JWKS público del proyecto (`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`) vía `PyJWKClient` de PyJWT, que cachea la llave pública en memoria — sigue sin requerir una llamada de red por cada request (cumple RNF-001 igual), y además es más simple: no hay ningún secreto que guardar para esta verificación. Requiere el extra `pyjwt[crypto]` (paquete `cryptography`) para soportar ES256.

**Corrección tras implementar (grupo 5 / autorización por rol)**: la verificación fallaba de forma intermitente con `ImmatureSignatureError: The token is not yet valid (iat)` — un desfase de pocos segundos entre el reloj de la máquina de desarrollo y el de Supabase hacía que el token pareciera emitido "en el futuro". PyJWT no tolera ningún desfase por defecto. Se agregó `leeway=10` (segundos) a `jwt.decode`, suficiente para absorber un desfase de reloj razonable sin debilitar la verificación de expiración real de los tokens.

### 10. Validación de entrada y prevención de inyección SQL
Todos los endpoints nuevos reciben su payload a través de modelos Pydantic con tipos y longitudes explícitas (p. ej. código TOTP como `str` de exactamente 6 dígitos numéricos), y todo acceso a nuestras propias tablas pasa por SQLAlchemy con parámetros bindeados — nunca interpolación de strings SQL.

**Análisis estático (28-09-2026, tarea 8.3).** Se corrió `bandit -r src` (seguridad Python), `pip-audit -r requirements.txt` y `npm audit` (frontend): 0 vulnerabilidades en dependencias de ambos lados. Bandit marcó 8 hallazgos medium/low (`B608`, posible inyección SQL) en `auth/repository.py`, `flota/repository.py` y `pedidos/repository.py`, todos por el mismo patrón: `text(f"... {columna} ...")` con el nombre de columna interpolado en el SQL en vez de bindeado (los bind params de SQLAlchemy solo cubren valores, no identificadores). Se revisó cada uno: en todos los casos el nombre interpolado sale de una constante fija del módulo (`_CONTADORES`, `_COLUMNAS`) o de las claves de un `dict` producido por `Pydantic.model_dump()` sobre un modelo con campos declarados (`flota/repository.py:actualizar`) — nunca de una clave o valor arbitrario del cuerpo de la petición. Se concluye que son falsos positivos (el patrón de Bandit no distingue de dónde viene el fragmento interpolado); no se abre ninguna corrección. **0 vulnerabilidades críticas confirmadas**, conforme al DoD global del proyecto.

## Risks / Trade-offs

- **[Riesgo] Nuestra tabla `sesiones_activas` puede quedar desactualizada en el listado si una sesión vence o Supabase la revoca sin que el usuario vuelva a intentar renovarla** → Mitigación: es solo un problema de presentación (sin refresh válido no hay tokens nuevos, y el access token vence a los 15 min); un job de sincronización marca `EXPIRADA` las sesiones sin actividad más allá de la vigencia del refresh token, y otro borra las cerradas con más de 30 días.
- **[Riesgo] Supabase no rechaza refresh tokens ya rotados** (comprobado con el ajuste "Detect and revoke potentially compromised refresh tokens" activo y guardado) → Mitigación: la detección de reuso es propia (hash del token vigente y del anterior + ventana de gracia, Decisión 5) y **nuestra API nunca reenvía a Supabase un token que no sea el vigente o el anterior en gracia**. Limitación residual: quien tenga un refresh token viejo puede seguir usándolo directamente contra Supabase (obteniendo tokens que nuestra API rechaza, porque la sesión queda `REVOCADA` o el token no es el vigente).
- **[Riesgo] El bloqueo RN-001 (3 intentos) solo se aplica a los logins que pasan por nuestra API.** La `anon key` es pública, así que un atacante puede adivinar contraseñas llamando a Supabase Auth directamente, sin contador nuestro (solo con el rate limiting genérico de Supabase por IP). Un token así no sirve contra nuestra API (su sesión no está registrada), pero la contraseña adivinada sí podría usarse después en nuestro login, con un solo intento → Mitigación parcial: MFA para roles con privilegios; contraseñas robustas; rate limiting de Supabase. Cerrarlo del todo requeriría no exponer el endpoint de contraseña de Supabase, algo que un proyecto Supabase estándar no permite; se documenta como limitación conocida.
- **[Riesgo] Un `access token` vencido más un refresh token ya usado de otra cuenta podrían usarse para forzar el incremento de `token_version` de la primera** (denegación de servicio dirigida) → Requiere poseer un access token real de la víctima y un refresh token propio ya usado; el impacto es un cierre de sesión forzado, sin acceso a datos. Se acepta para el MVP.
- **[Riesgo] Cambio de contrato del endpoint de login (BREAKING)** → Mitigación: dado que HU-001 nunca se implementó en código todavía, el impacto real es cero en este momento.
- **[Trade-off] Delegar identidad a Supabase reduce código propio pero introduce una dependencia externa crítica** → Aceptado: el equipo ya depende de Supabase para la base de datos; la superficie de riesgo adicional por depender también de su Auth es marginal, y el ahorro de desarrollo es significativo.
- **[Riesgo] El Custom Access Token Hook de Supabase (Decisión 6) parece cachear el `token_version` que lee de `usuarios`, en vez de leerlo fresco en cada emisión de token.** Observado repetidamente el 28-09-2026: tras `revocar_todas` (que incrementa `token_version`), un login inmediatamente posterior seguía recibiendo un JWT con el `ver` anterior, y `get_current_user` lo rechazaba con "Token revocado, inicia sesión de nuevo" — incluso para una cuenta que nunca había iniciado sesión con ese token. Forzar `token_version = 1` en la fila (el valor con el que se creó la cuenta) hace que el hook vuelva a coincidir, lo que sugiere que cachea el primer valor que vio y no se refresca solo. Impacto: cualquier usuario real que use "cerrar todas las sesiones" (o gatille la detección de reuso de refresh token) podría quedar sin poder iniciar sesión de nuevo hasta que el caché expire o se corrija a mano. → Mitigación pendiente: revisar en el panel de Supabase (Authentication → Hooks → el hook de Custom Access Token) si tiene alguna opción de caché de resultado activada y desactivarla antes de producción; si el comportamiento persiste sin esa opción, es una limitación de la plataforma a reportar a Supabase.

## Migration Plan

1. En el panel de Supabase: configurar la expiración del token de acceso a 15 minutos, habilitar el proveedor de email/password, y crear el Custom Access Token Hook de la Decisión 6 (activarlo solo después de que exista `usuarios.token_version`, o el login falla).
2. Aplicar la migración SQL que ajusta `usuarios` (agrega columnas nuevas, quita `password_hash`, la PK ahora referencia `auth.users`) y crea `sesiones_activas`, habilitando RLS con sus políticas — migración reversible.
3. Desplegar el backend con los nuevos endpoints (`/api/auth/mfa/*`, `/api/auth/sesiones/*`) que orquestan Supabase Auth.
4. Desplegar el frontend con las pantallas de enrolamiento/verificación TOTP y el manejo del estado `mfa_required`, hablando siempre contra nuestra propia API.
5. Rollback: revertir el despliegue de backend/frontend y ejecutar la down-migration; dado que el sistema aún no tiene usuarios reales, no hay migración de datos que revertir.

## Open Questions

- ¿Se requerirán códigos de recuperación (backup codes) de un solo uso para MFA en una iteración posterior? Supabase Auth no los ofrece de forma nativa para TOTP; quedaría como una mejora futura fuera del alcance de este cambio.
- ~~¿El plan gratuito de Supabase permite configurar el Custom Access Token Hook sin restricciones?~~ **Resuelto**: sí, disponible en el plan Free del proyecto (Authentication → Auth Hooks, marcado como "BETA" pero funcional). La función SQL `custom_access_token_hook` ya fue creada; el hook se activa formalmente al finalizar la migración de `usuarios` (grupo 2 de tasks.md), para no romper el login mientras esa tabla no existe.
