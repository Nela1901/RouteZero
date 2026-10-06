# route-planning Specification

## Purpose
Define cómo el Administrador solicita, revisa, confirma o descarta las rutas de una jornada, y qué información recibe, de modo que las rutas solo lleguen a los conductores después de una revisión humana.

## Requirements

### Requirement: Generación de rutas en borrador
El sistema SHALL permitir que un Administrador solicite la generación de rutas para una fecha de jornada igual o posterior a hoy, creando las rutas con estado PLANIFICADA (borrador) agrupadas en un lote, sin modificar el estado de los pedidos.

#### Scenario: Generación exitosa
- **WHEN** el Administrador solicita rutas para una fecha con pedidos pendientes y recursos disponibles
- **THEN** el sistema crea las rutas en estado PLANIFICADA bajo un nuevo lote, los pedidos siguen en estado PENDIENTE y la respuesta incluye las rutas con sus paradas, las métricas y el tiempo de ejecución

#### Scenario: Fecha pasada
- **WHEN** el Administrador solicita rutas para una fecha anterior a hoy
- **THEN** el sistema rechaza la solicitud indicando que la fecha de jornada no puede ser pasada

#### Scenario: Acceso restringido
- **WHEN** un usuario que no es Administrador solicita la generación de rutas
- **THEN** el sistema rechaza la solicitud por falta de permisos

### Requirement: Contenido del resultado
El sistema SHALL devolver, para cada ruta, el vehículo, el conductor, la distancia total, el tiempo total, las emisiones de CO₂, el combustible estimado, el porcentaje de entregas dentro de ventana y las paradas ordenadas con su hora estimada de llegada; y SHALL indicar la fuente de distancias usada y la mejora respecto de la solución inicial.

#### Scenario: Resultado completo
- **WHEN** finaliza una generación
- **THEN** cada ruta de la respuesta incluye sus métricas y sus paradas en orden, y la respuesta incluye la fuente de distancias y la comparación con la solución inicial

### Requirement: Regeneración que solo reemplaza borradores
El sistema SHALL reemplazar, al generar rutas para una fecha, únicamente los borradores PLANIFICADA de esa misma fecha, y SHALL conservar sin cambios las rutas ya CONFIRMADA.

#### Scenario: Regenerar sobre un borrador
- **WHEN** existe un borrador para la fecha y el Administrador vuelve a generar rutas
- **THEN** el borrador anterior se elimina y se crea uno nuevo en un único paso atómico

#### Scenario: Rutas confirmadas intactas
- **WHEN** existen rutas CONFIRMADA para la fecha y se genera un nuevo borrador
- **THEN** las rutas confirmadas y sus pedidos permanecen sin cambios, y el nuevo borrador solo considera pedidos aún PENDIENTE

### Requirement: Recursos comprometidos en rutas confirmadas
El sistema SHALL excluir de una nueva generación a los vehículos y a los conductores que ya tienen una ruta CONFIRMADA o EN_EJECUCION en la misma fecha de jornada, de modo que ningún vehículo ni conductor se asigne dos veces el mismo día; los borradores PLANIFICADA no comprometen recursos porque se reemplazan al regenerar.

#### Scenario: Vehículo y conductor ya confirmados
- **WHEN** existe una ruta CONFIRMADA para la fecha con un vehículo y un conductor, y se genera un nuevo borrador para esa fecha
- **THEN** el nuevo borrador no usa ese vehículo ni ese conductor

#### Scenario: Sin recursos libres
- **WHEN** todos los vehículos o todos los conductores elegibles ya están comprometidos en rutas confirmadas de la fecha
- **THEN** el sistema informa que no es posible generar rutas, deja los pedidos nuevos sin cobertura por falta de recursos y conserva lo ya confirmado

#### Scenario: Otra fecha
- **WHEN** los recursos están comprometidos para una fecha y se genera un borrador para otra fecha
- **THEN** esos recursos siguen disponibles para la otra fecha

### Requirement: Confirmación de rutas
El sistema SHALL permitir que el Administrador confirme un lote de borradores, pasando sus rutas a estado CONFIRMADA y sus pedidos a estado ASIGNADO, siempre que todos los pedidos del lote sigan en estado PENDIENTE.

#### Scenario: Confirmación exitosa
- **WHEN** el Administrador confirma un lote cuyos pedidos siguen pendientes
- **THEN** las rutas pasan a CONFIRMADA, los pedidos a ASIGNADO y la operación se registra en la auditoría

#### Scenario: Pedido cancelado durante la revisión
- **WHEN** un pedido del lote fue cancelado después de generar el borrador
- **THEN** el sistema rechaza la confirmación, identifica los pedidos afectados e indica que debe regenerar las rutas

### Requirement: Descarte de borradores
El sistema SHALL permitir que el Administrador descarte un lote de borradores, eliminando sus rutas y dejando los pedidos como estaban, y SHALL rechazar el descarte de rutas ya confirmadas.

#### Scenario: Descarte de un borrador
- **WHEN** el Administrador descarta un lote en estado PLANIFICADA
- **THEN** sus rutas se eliminan y los pedidos siguen en PENDIENTE

#### Scenario: Descarte de rutas confirmadas
- **WHEN** el Administrador intenta descartar un lote ya CONFIRMADA
- **THEN** el sistema rechaza la operación indicando que las rutas confirmadas no pueden descartarse

### Requirement: Consulta de rutas
El sistema SHALL permitir que Administradores y Operadores consulten las rutas de una fecha y el detalle de una ruta, y SHALL negar esa consulta a los demás roles.

#### Scenario: Operador consulta
- **WHEN** un Operador consulta las rutas de una fecha
- **THEN** el sistema devuelve las rutas con su estado, vehículo, conductor y métricas

#### Scenario: Conductor sin acceso
- **WHEN** un usuario con rol Conductor consulta el listado de rutas
- **THEN** el sistema rechaza la solicitud por falta de permisos

### Requirement: Una generación a la vez
El sistema SHALL atender una sola generación de rutas a la vez y SHALL rechazar una segunda solicitud simultánea con un mensaje que indique que hay una generación en curso, para no agotar la CPU del servidor.

#### Scenario: Solicitud simultánea
- **WHEN** llega una segunda solicitud de generación mientras otra sigue en ejecución
- **THEN** el sistema responde con un conflicto indicando que hay una generación en curso

### Requirement: Registro de métricas y auditoría
El sistema SHALL guardar por cada ruta sus métricas de sostenibilidad (emisiones de CO₂, combustible, distancia y cumplimiento de ventanas) y SHALL registrar en la auditoría la generación, confirmación y descarte de rutas, identificando al usuario y el lote, sin datos personales de conductores.

#### Scenario: Auditoría de la confirmación
- **WHEN** un Administrador confirma un lote
- **THEN** queda un registro de auditoría con el usuario, la acción y el identificador del lote
