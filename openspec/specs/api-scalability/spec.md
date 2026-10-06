# api-scalability Specification

## Purpose
Define los límites de rendimiento y la estructura de la API para que el sistema soporte hasta 1,000 pedidos diarios sin degradar su tiempo de respuesta (RNF-008, HT-08).

## Requirements

### Requirement: Listados paginados
El sistema SHALL devolver el listado de pedidos paginado, aceptando un límite de resultados (50 por defecto y 200 como máximo) y un desplazamiento, e SHALL incluir en la respuesta el total de registros que cumplen el filtro.

#### Scenario: Página por defecto
- **WHEN** se consulta el listado de pedidos sin parámetros de paginación
- **THEN** la respuesta contiene como máximo 50 pedidos y el total de pedidos que cumplen el filtro

#### Scenario: Límite excesivo
- **WHEN** se solicita un límite mayor que 200
- **THEN** el sistema rechaza la solicitud indicando el máximo permitido

### Requirement: Tiempo de respuesta con carga máxima
El sistema SHALL responder en 2 segundos o menos en el percentil 95 a las operaciones de consulta, registro y cancelación de pedidos cuando existan 1,000 pedidos en la base de datos.

#### Scenario: Consulta con 1,000 pedidos
- **WHEN** existen 1,000 pedidos registrados y se consulta una página del listado
- **THEN** el percentil 95 del tiempo de respuesta es de 2 segundos o menos

### Requirement: Módulos independientes
El sistema SHALL organizar el backend en módulos por característica (autenticación, flota, conductores, clientes, pedidos, rutas, red vial y algoritmo) sin dependencias directas entre los módulos de negocio; los módulos solo SHALL compartir el núcleo común (`core`, que incluye la validación de la zona de cobertura) y el registro de auditoría (`auditoria`), y, en el caso de rutas, los módulos de red vial y algoritmo.

#### Scenario: Verificación de dependencias
- **WHEN** se analizan las importaciones del código fuente del backend
- **THEN** ningún módulo de negocio importa código de otro módulo de negocio (salvo `core` y `auditoria`), y el módulo `algoritmo` no importa FastAPI, SQLAlchemy ni ningún otro módulo del backend
