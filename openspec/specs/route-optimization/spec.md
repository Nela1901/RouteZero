# route-optimization Specification

## Purpose
Define el comportamiento del motor que decide qué vehículo y qué conductor atienden cada pedido y en qué orden, minimizando distancia, combustible, emisiones de CO₂ y entregas tardías, dentro de las restricciones operativas y normativas de Andina Reparto S.A.C.

## Requirements

### Requirement: Planificación con flota heterogénea y ventanas de tiempo
El sistema SHALL planificar, para una fecha de jornada, la asignación de los pedidos pendientes a rutas de vehículos disponibles saliendo y regresando a un único depósito, considerando para cada vehículo su capacidad, consumo y factor de emisión, y para cada pedido su peso, su prioridad y su ventana de entrega.

#### Scenario: Solución válida para un conjunto de pedidos
- **WHEN** existen pedidos pendientes, vehículos disponibles y conductores elegibles para la fecha
- **THEN** el motor devuelve rutas en las que cada pedido atendido aparece exactamente una vez y cada ruta pertenece a un único vehículo y un único conductor

### Requirement: Capacidad máxima del vehículo
El sistema SHALL garantizar que la suma de los pesos de los pedidos asignados a una ruta no supere la capacidad de carga registrada del vehículo (RN-005).

#### Scenario: Capacidad respetada
- **WHEN** el motor genera rutas para pedidos cuya suma de pesos excede la capacidad de un solo vehículo
- **THEN** ninguna ruta devuelta supera la capacidad de su vehículo y los pedidos que no caben en ninguna ruta se informan sin cobertura

### Requirement: Jornada máxima y descanso del conductor
El sistema SHALL garantizar que la duración de una ruta, incluidos los tiempos de atención y los descansos, no supere 8 horas ni salga del horario de disponibilidad del conductor, e SHALL incluir un descanso de 60 minutos cuando se acumulen 4 horas de trabajo continuo (RN-002, RN-003).

#### Scenario: Ruta dentro de la jornada
- **WHEN** el motor construye una ruta para un conductor con disponibilidad de 06:00 a 14:00
- **THEN** la hora estimada de regreso al depósito, incluidos los descansos, no supera las 14:00 ni las 8 horas de duración

#### Scenario: Descanso tras cuatro horas
- **WHEN** una ruta acumula 4 horas de conducción y atención sin pausa
- **THEN** el itinerario incluye un descanso de 60 minutos antes de continuar

### Requirement: Ventanas de tiempo con penalización
El sistema SHALL tratar la ventana de entrega de cada pedido como restricción blanda: SHALL esperar en el lugar si el vehículo llega antes de que abra la ventana, y SHALL penalizar en la función objetivo cada minuto de retraso respecto del cierre de la ventana (RN-006).

#### Scenario: Llegada antes de la ventana
- **WHEN** el vehículo llega a un cliente antes de la hora de apertura de su ventana
- **THEN** la hora de entrega estimada es la hora de apertura y no se aplica penalización

#### Scenario: Entrega tardía
- **WHEN** una entrega solo es posible después del cierre de su ventana
- **THEN** se acepta la solución con la penalización correspondiente y el pedido se marca como tardío en el resultado

### Requirement: Prioridad de pedidos express
El sistema SHALL dar a los pedidos EXPRESS la mayor ponderación de penalización por retraso y SHALL entregarlos antes que los pedidos ESTANDAR y ECONOMICO dentro de la misma ruta (RN-008).

#### Scenario: Express antes que estándar
- **WHEN** una misma ruta contiene pedidos EXPRESS y ESTANDAR
- **THEN** las paradas EXPRESS ocupan las primeras posiciones de la ruta

### Requirement: Elegibilidad de vehículos y conductores
El sistema SHALL considerar únicamente vehículos en estado DISPONIBLE y conductores marcados como disponibles cuya licencia siga vigente en la fecha de la jornada, y SHALL emparejar cada vehículo solo con conductores cuya categoría de licencia sea compatible con su tipo.

#### Scenario: Licencia vencida
- **WHEN** la fecha de vencimiento de la licencia de un conductor es anterior o igual a la fecha de la jornada
- **THEN** ese conductor no se asigna a ninguna ruta

#### Scenario: Categoría incompatible
- **WHEN** un conductor solo tiene licencia de moto y el único vehículo libre es una furgoneta
- **THEN** no se forma esa pareja y la furgoneta no recibe ruta

### Requirement: Restricción de circulación configurable
El sistema SHALL excluir de la planificación a los vehículos alcanzados por una restricción de circulación vigente para la fecha de la jornada cuando exista una tabla de restricción por último dígito de placa configurada, y SHALL operar sin restricción alguna mientras no se configure ninguna tabla (RN-004).

#### Scenario: Sin tabla configurada
- **WHEN** no existe ninguna tabla de restricción por placa
- **THEN** ningún vehículo se excluye por su placa

#### Scenario: Vehículo restringido ese día
- **WHEN** existe una tabla que restringe el último dígito de placa de un vehículo en la fecha de la jornada
- **THEN** ese vehículo no recibe ruta ese día

### Requirement: Función objetivo ecológica
El sistema SHALL minimizar una suma ponderada de distancia recorrida, combustible consumido (distancia dividida por el consumo en km/L del vehículo), emisiones de CO₂ (distancia por el factor de emisión del vehículo, RN-009) y penalizaciones por retraso, con pesos configurables.

#### Scenario: Preferencia por el vehículo más eficiente
- **WHEN** dos vehículos con distinto factor de emisión pueden atender las mismas paradas con la misma distancia
- **THEN** el motor prefiere asignarlas al vehículo de menor emisión

### Requirement: Límite de tiempo de optimización
El sistema SHALL devolver una solución válida en un máximo de 45 segundos para hasta 150 pedidos y 15 vehículos (RN-015), terminando la búsqueda al agotar un presupuesto de tiempo configurable (30 segundos por defecto, 40 como máximo) y devolviendo la mejor solución encontrada hasta ese momento.

#### Scenario: Presupuesto agotado
- **WHEN** la búsqueda alcanza el presupuesto de tiempo antes de converger
- **THEN** el sistema devuelve la mejor solución válida encontrada, sin superar los 45 segundos totales

#### Scenario: Rendimiento con la carga máxima
- **WHEN** se ejecuta el motor con 150 pedidos y 15 vehículos
- **THEN** el percentil 95 del tiempo total de generación no supera los 45 segundos

### Requirement: Mejora sobre la solución inicial
El sistema SHALL construir primero una solución inicial voraz válida y SHALL devolver una solución con un costo igual o menor que ella, informando el porcentaje de mejora de distancia y de emisiones respecto de esa línea base.

#### Scenario: Nunca peor que la línea base
- **WHEN** el motor termina cualquier ejecución
- **THEN** el costo de la solución devuelta no supera el de la solución voraz inicial

### Requirement: Pedidos sin cobertura
El sistema SHALL informar, para cada pedido que no pudo asignarse, el motivo (peso mayor que la capacidad de cualquier vehículo, falta de vehículos o conductores elegibles, o falta de tiempo dentro de la jornada), e SHALL sugerir acciones correctivas.

#### Scenario: Pedido más pesado que toda la flota
- **WHEN** el peso de un pedido supera la capacidad del vehículo más grande disponible
- **THEN** el pedido aparece sin cobertura con el motivo de capacidad y la sugerencia de dividirlo o de incorporar un vehículo mayor

#### Scenario: Sin vehículos disponibles
- **WHEN** no hay ningún vehículo disponible o ningún conductor elegible
- **THEN** el sistema informa que no es posible generar rutas, lista todos los pedidos como sin cobertura y sugiere revisar la flota y los conductores

### Requirement: Reproducibilidad
El sistema SHALL producir el mismo resultado para los mismos datos de entrada y la misma semilla aleatoria, siempre que la búsqueda no termine por tiempo.

#### Scenario: Misma semilla
- **WHEN** se ejecuta el motor dos veces con los mismos datos, la misma semilla y un presupuesto de iteraciones fijo
- **THEN** ambas ejecuciones devuelven rutas idénticas
