# Spec Delta

## Purpose

Define el ciclo de vida de las sesiones autenticadas de RouteZero: emisión de tokens de acceso y refresco, y la capacidad de los usuarios de consultar y revocar sus propias sesiones activas, incluyendo su dispositivo e información de acceso.

## ADDED Requirements

### Requirement: Emisión de par de tokens al completar la autenticación
El sistema SHALL emitir un token de acceso de corta duración (15 minutos) y un token de refresco al completar exitosamente el proceso de autenticación (con o sin segundo factor), y SHALL registrar una entrada visible para el usuario en su listado de sesiones activas en ese momento.

#### Scenario: Emisión exitosa tras login completo
- **WHEN** un usuario completa el proceso de autenticación (login simple, o login + código TOTP si tiene MFA activo)
- **THEN** el sistema emite un token de acceso válido por 15 minutos y un token de refresco, y registra la nueva sesión activa con su información de dispositivo

### Requirement: Renovación del token de acceso mediante token de refresco
El sistema SHALL permitir obtener un nuevo token de acceso presentando un token de refresco válido y no revocado.

#### Scenario: Renovación exitosa
- **WHEN** el cliente presenta un token de refresco vigente
- **THEN** el sistema emite un nuevo token de acceso y actualiza la fecha de último uso de la sesión correspondiente

#### Scenario: Token de refresco inválido o revocado
- **WHEN** el cliente presenta un token de refresco expirado o previamente revocado
- **THEN** el sistema rechaza la renovación y exige un nuevo inicio de sesión completo

### Requirement: Detección de reutilización de token de refresco
El sistema SHALL tratar la reutilización de un token de refresco ya invalidado como un indicio de robo de sesión: al detectarse, SHALL revocar la sesión afectada y reflejar ese estado en el listado de sesiones activas del usuario en su siguiente consulta.

#### Scenario: Reutilización detectada
- **WHEN** se presenta un token de refresco que ya había sido invalidado previamente
- **THEN** el sistema rechaza la solicitud, marca la sesión correspondiente como revocada, y registra el evento como incidente de seguridad

### Requirement: Revocación inmediata de tokens de acceso ya emitidos
El sistema SHALL asociar a cada cuenta un número de versión de sesión, embebido como reclamo en cada token de acceso emitido, de modo que incrementar esa versión invalide de inmediato todos los tokens de acceso ya emitidos con una versión anterior, sin esperar a su expiración natural de 15 minutos.

#### Scenario: Token de acceso rechazado tras incremento de versión
- **WHEN** se presenta un token de acceso cuyo reclamo de versión no coincide con la versión de sesión vigente de la cuenta
- **THEN** el sistema rechaza el token como inválido, independientemente de que su tiempo de expiración declarado aún no se haya cumplido

#### Scenario: Incremento de versión al cerrar todas las sesiones
- **WHEN** un usuario solicita cerrar todas sus sesiones activas, o el sistema detecta reutilización de un token de refresco
- **THEN** el sistema incrementa la versión de sesión de la cuenta, de modo que cualquier token de acceso emitido antes de esa acción también deja de ser válido

### Requirement: Consulta de sesiones activas propias
El sistema SHALL permitir a un usuario autenticado listar únicamente sus propias sesiones activas, incluyendo información del dispositivo/cliente, fecha de creación y fecha de último uso.

#### Scenario: Listado exitoso
- **WHEN** un usuario autenticado solicita el listado de sus sesiones activas
- **THEN** el sistema devuelve únicamente las sesiones asociadas a su propia cuenta, sin exponer sesiones de otros usuarios

### Requirement: Revocación de una sesión específica
El sistema SHALL permitir a un usuario autenticado cerrar una de sus propias sesiones activas de forma remota.

#### Scenario: Revocación de sesión propia
- **WHEN** un usuario solicita cerrar una sesión activa que le pertenece
- **THEN** el sistema invalida esa sesión y la marca como cerrada, sin afectar sus otras sesiones activas

#### Scenario: Intento de revocar sesión ajena
- **WHEN** un usuario solicita cerrar una sesión activa que pertenece a otra cuenta
- **THEN** el sistema deniega la operación independientemente del rol del solicitante

### Requirement: Revocación de todas las sesiones propias
El sistema SHALL permitir a un usuario autenticado cerrar todas sus sesiones activas en una sola operación (por ejemplo, tras sospechar de un acceso no autorizado).

#### Scenario: Cierre total exitoso
- **WHEN** un usuario autenticado solicita cerrar todas sus sesiones activas
- **THEN** el sistema invalida todas sus sesiones y marca cada una como cerrada

### Requirement: Reflejo del estado real de expiración de sesiones
El sistema SHALL marcar como expirada, en el listado visible al usuario, cualquier sesión cuyo token de refresco ya no sea válido, sin requerir una acción manual del usuario.

#### Scenario: Expiración reflejada en el listado
- **WHEN** una sesión deja de tener un token de refresco válido (por vencimiento o revocación)
- **THEN** el listado de sesiones del usuario la muestra como expirada o cerrada en su siguiente consulta, en vez de como activa
