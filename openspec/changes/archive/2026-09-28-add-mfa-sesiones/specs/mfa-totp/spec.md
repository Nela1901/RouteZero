# Spec Delta

## Purpose

Define el comportamiento de la autenticación multifactor (MFA) basada en códigos TOTP como segundo factor obligatorio para las cuentas que lo activan, y opcional para el resto de usuarios de RouteZero.

## ADDED Requirements

### Requirement: Inscripción de MFA por TOTP
El sistema SHALL permitir que un usuario autenticado inicie la inscripción de MFA, generando un secreto TOTP único asociado a su cuenta y presentándolo como código QR para su registro en una aplicación autenticadora compatible con RFC 6238.

#### Scenario: Inicio de inscripción exitoso
- **WHEN** un usuario autenticado sin MFA activo solicita inscribirse en MFA
- **THEN** el sistema genera un secreto TOTP nuevo, lo asocia a la cuenta en estado "pendiente de confirmación" y devuelve un código QR para escanear

#### Scenario: Inscripción rechazada si ya existe MFA activo
- **WHEN** un usuario con MFA ya activo intenta iniciar una nueva inscripción
- **THEN** el sistema rechaza la solicitud e indica que debe desactivar el MFA actual antes de inscribir uno nuevo

### Requirement: Confirmación de inscripción de MFA
El sistema SHALL exigir que el usuario ingrese un código TOTP válido generado con el secreto recién inscrito antes de marcar el MFA como activo en la cuenta.

El sistema SHALL aceptar como válido un código TOTP correspondiente al paso de tiempo actual (30 segundos) o al paso inmediatamente anterior (tolerancia de ±1 paso, ventana total de 90 segundos), para absorber un desfase de reloj razonable entre el servidor y la aplicación autenticadora sin ampliar significativamente la ventana explotable por fuerza bruta.

#### Scenario: Confirmación exitosa
- **WHEN** el usuario envía un código TOTP de 6 dígitos válido correspondiente al secreto en estado "pendiente de confirmación", dentro de la ventana de tolerancia de ±1 paso
- **THEN** el sistema activa el MFA en la cuenta y descarta cualquier secreto pendiente anterior

#### Scenario: Código de confirmación inválido
- **WHEN** el usuario envía un código TOTP incorrecto o expirado durante la confirmación
- **THEN** el sistema rechaza la activación, mantiene el MFA en estado "pendiente de confirmación" e informa que el código no es válido

### Requirement: Segundo factor obligatorio en el login
El sistema SHALL exigir un código TOTP válido antes de emitir tokens de sesión cuando la cuenta que inicia sesión tiene MFA activo.

#### Scenario: Login con MFA activo requiere segundo paso
- **WHEN** un usuario con MFA activo envía credenciales (correo y contraseña) válidas
- **THEN** el sistema responde con un estado intermedio `mfa_required` y no emite tokens de acceso ni de refresco hasta recibir un código TOTP válido

#### Scenario: Login completo tras código TOTP válido
- **WHEN** un usuario en estado `mfa_required` envía un código TOTP válido dentro de la ventana de tolerancia de ±1 paso (90 segundos)
- **THEN** el sistema emite el par de tokens de sesión y redirige al módulo correspondiente a su rol

#### Scenario: Código TOTP inválido durante login
- **WHEN** un usuario en estado `mfa_required` envía un código TOTP incorrecto o expirado
- **THEN** el sistema rechaza la solicitud, no emite tokens y muestra un mensaje indicando que el código es inválido

### Requirement: Bloqueo por intentos fallidos de código TOTP
El sistema SHALL bloquear temporalmente la verificación de MFA de una cuenta tras 3 intentos consecutivos de código TOTP inválido. Este contador de intentos fallidos SHALL ser independiente del contador de bloqueo por contraseña ya existente (RN-001): se registra por separado (asociado al secreto MFA de la cuenta, no a sus credenciales de acceso), de modo que agotar los intentos de un factor no bloquea ni comparte estado con el otro.

#### Scenario: Bloqueo tras intentos fallidos de MFA
- **WHEN** una cuenta en estado `mfa_required` recibe 3 códigos TOTP inválidos consecutivos
- **THEN** el sistema bloquea la verificación de MFA de esa cuenta por 15 minutos, registra el evento como intento de seguridad y muestra el tiempo de bloqueo restante

### Requirement: Desactivación de MFA
El sistema SHALL permitir que un usuario con MFA activo lo desactive únicamente tras reautenticarse con su contraseña y un código TOTP válido vigente.

#### Scenario: Desactivación exitosa
- **WHEN** un usuario con MFA activo envía su contraseña actual y un código TOTP válido junto con la solicitud de desactivación
- **THEN** el sistema desactiva el MFA, elimina el secreto TOTP asociado y registra el evento en la auditoría

#### Scenario: Desactivación rechazada por verificación fallida
- **WHEN** un usuario intenta desactivar su MFA sin una contraseña o código TOTP válidos
- **THEN** el sistema rechaza la desactivación y mantiene el MFA activo

### Requirement: Aislamiento del secreto MFA por usuario
El sistema SHALL garantizar que ningún usuario, incluyendo usuarios autenticados con otros roles, pueda leer o listar el secreto TOTP de otra cuenta a través de ninguna interfaz de la API.

#### Scenario: Intento de acceso al secreto de otra cuenta
- **WHEN** un usuario autenticado solicita el secreto o estado detallado de MFA de una cuenta distinta a la suya
- **THEN** el sistema deniega el acceso independientemente del rol del solicitante, salvo el estado público "MFA activo/inactivo" visible para administración
