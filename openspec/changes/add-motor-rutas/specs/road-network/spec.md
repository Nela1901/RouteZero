# Spec Delta

## Purpose

Define cómo el sistema obtiene las distancias y los tiempos de viaje entre el depósito y los puntos de entrega usando la red de calles de Huancayo, de modo que las rutas se calculen sobre recorridos reales y no sobre líneas rectas.

## ADDED Requirements

### Requirement: Red vial derivada de OpenStreetMap
El sistema SHALL calcular distancias y tiempos de viaje sobre un grafo dirigido de las calles de la zona urbana de Huancayo construido a partir de datos de OpenStreetMap, respetando los sentidos únicos de las vías, y SHALL distribuirlo como un archivo versionado junto con el código para que su uso en ejecución no dependa de ningún servicio externo.

#### Scenario: Cálculo de matriz por calles reales
- **WHEN** el sistema necesita las distancias entre el depósito y N puntos de entrega dentro de la zona de cobertura
- **THEN** devuelve una matriz de distancias (metros) y otra de tiempos (segundos) calculadas por el camino más corto sobre el grafo, sin realizar ninguna llamada de red

#### Scenario: Sentidos únicos respetados
- **WHEN** una calle está marcada como de sentido único en el grafo
- **THEN** el camino más corto entre dos puntos nunca la recorre en sentido contrario

### Requirement: Asignación de cada punto al nodo de calle más cercano
El sistema SHALL asignar cada punto de entrega y el depósito al nodo más cercano de la red vial principal conectada, y SHALL tratar como no resoluble por calles todo punto cuyo nodo más cercano esté a más de 500 metros.

#### Scenario: Punto dentro de la zona de la red
- **WHEN** un pedido tiene coordenadas dentro de la zona de cobertura y a menos de 500 metros de una calle del grafo
- **THEN** se le asigna el nodo más cercano de la red principal y participa en la matriz por calles

#### Scenario: Punto lejos de toda calle
- **WHEN** un pedido tiene coordenadas a más de 500 metros del nodo más cercano
- **THEN** el sistema calcula sus distancias en línea recta multiplicadas por 1.35 y deja constancia de ello en el resultado

### Requirement: Respaldo en línea recta
El sistema SHALL calcular las distancias como la distancia en línea recta multiplicada por 1.35 cuando el archivo del grafo no esté disponible o no pueda cargarse, y SHALL informar en el resultado de cada generación qué fuente de distancias se usó.

#### Scenario: Archivo del grafo ausente
- **WHEN** el archivo del grafo no existe o está dañado al iniciar la generación de rutas
- **THEN** el sistema continúa con el respaldo en línea recta y marca la fuente de distancias como "aproximada" en la respuesta

### Requirement: Tiempo de viaje por tipo de vía
El sistema SHALL estimar el tiempo de recorrido de cada tramo con una velocidad base por tipo de vía, alineada con los límites del Reglamento Nacional de Tránsito (DS 033-2001-MTC, art. 162: 40 km/h en calles y jirones, 60 km/h en avenidas), multiplicada por un factor de velocidad urbana configurable.

#### Scenario: Velocidad según tipo de vía
- **WHEN** se calcula el tiempo de un tramo de avenida y el de un tramo de calle residencial de igual longitud
- **THEN** el tiempo del tramo de avenida es menor que el del tramo residencial

### Requirement: Rendimiento del cálculo de matrices
El sistema SHALL calcular la matriz de distancias y tiempos para 150 pedidos y el depósito en menos de 5 segundos sobre la configuración de despliegue, y SHALL mantener el consumo adicional de memoria del cálculo por debajo de 100 MB.

#### Scenario: Matriz de 151 × 151 puntos
- **WHEN** se solicita la matriz para 150 pedidos y el depósito
- **THEN** el cálculo termina en menos de 5 segundos y sin superar 100 MB de memoria adicional

### Requirement: Atribución de la fuente de datos
El sistema SHALL acreditar a OpenStreetMap como fuente de los datos de calles con el texto "© OpenStreetMap contributors" en la documentación del proyecto y en cualquier pantalla que muestre rutas sobre el mapa.

#### Scenario: Crédito visible
- **WHEN** se muestra un mapa con datos de OpenStreetMap
- **THEN** el crédito "© OpenStreetMap contributors" es visible para el usuario
