# 01 Transformando a Ágil

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha** | 2026-09-10 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../README.md)

---

## 1. Metodología de Transformación

Los Requerimientos Funcionales (RF) del archivo `06. Requisitos Funcionales V_1_0_0.md` fueron mapeados jerárquicamente hacia Épicas y descompuestos en Historias de Usuario (HU). Los Requerimientos No Funcionales (RNF) del archivo `07. Requisitos No Funcionales V_1_0_0.md` fueron transformados en Historias Técnicas (HT) de infraestructura, arquitectura, seguridad y rendimiento, e integrados transversalmente como Criterios de Aceptación y Definition of Done (DoD).

### Mapa de Transformación RF → Épicas

| Épica | RF Origen | Descripción |
|---|---|---|
| EP-01 Seguridad y Acceso | RF-011 | Autenticación, control de acceso por roles (RBAC) y auditoría — base del sistema |
| EP-02 Gestión de Flota | RF-001 | Registro y administración de vehículos de Andina Reparto S.A.C. |
| EP-03 Gestión de Pedidos | RF-002 | Registro y seguimiento de pedidos con coordenadas GPS y ventanas de tiempo |
| EP-04 Gestión de Personas | RF-008, RF-009 | Administración de conductores y clientes de Andina Reparto S.A.C. |
| EP-05 Optimización de Rutas | RF-003, RF-007 | Generación y re-optimización dinámica de rutas con ACO + Green VRP |
| EP-06 Visualización de Rutas | RF-004 | Mapa interactivo con Leaflet + OpenStreetMap para visualización de rutas |
| EP-07 Sostenibilidad | RF-005, RF-006, RF-010 | Dashboard de indicadores, reportes PDF y plan de compensación de carbono |

### Mapa de Transformación RNF → Historias Técnicas

| Historia Técnica | RNF Origen | Tipo | Épica |
|---|---|---|---|
| HT-01 Implementación OWASP Top 10 + JWT | RNF-003, RNF-004 | Seguridad | EP-01 |
| HT-02 Cifrado de datos y cumplimiento Ley N° 29733 | RNF-013 | Seguridad / Normativa | EP-01 |
| HT-03 Configuración de infraestructura Render + Vercel | RNF-005 | Infraestructura | EP-01 |
| HT-04 Pruebas unitarias del módulo de flota | — | Calidad / Testing | EP-02 |
| HT-05 Pruebas unitarias del módulo de pedidos | — | Calidad / Testing | EP-03 |
| HT-06 Pruebas unitarias del módulo de personas | — | Calidad / Testing | EP-04 |
| HT-07 Optimización del motor ACO | RNF-001, RNF-002 | Rendimiento | EP-05 |
| HT-08 Arquitectura escalable por características | RNF-008 | Arquitectura | EP-05 |
| HT-09 Diseño responsive y WCAG 2.1 AA | RNF-006, RNF-007 | Accesibilidad | EP-06 |
| HT-10 Pruebas de integración del mapa interactivo | — | Calidad / Testing | EP-06 |
| HT-11 Optimización de consultas SQL y Green Software | RNF-011 | Rendimiento / Sostenibilidad | EP-07 |
| HT-12 Pruebas de generación de reportes PDF | — | Calidad / Testing | EP-07 |

---

## 2. Épicas del Proyecto

### EP-01: Seguridad y Acceso
Autenticación JWT, control de acceso por roles (RBAC), bloqueo por intentos fallidos y registro de auditoría conforme a la Ley N° 29733. Es la base del sistema, ningún módulo es accesible sin autenticación previa.

### EP-02: Gestión de Flota
Administración completa de la flota de vehículos de Andina Reparto S.A.C., incluyendo registro, actualización y control de disponibilidad con métricas de emisión de CO₂.

### EP-03: Gestión de Pedidos
Registro, seguimiento y gestión de pedidos con coordenadas GPS, ventanas de tiempo y prioridades para el distrito de Huancayo.

### EP-04: Gestión de Personas
Administración de conductores con restricciones de jornada (Ley N° 30224) y gestión de clientes con preferencias de entrega.

### EP-05: Optimización de Rutas
Generación de rutas óptimas mediante el algoritmo ACO (Colonia de Hormigas) aplicando VRPTW + Green VRP, con re-optimización dinámica ante incidentes. Requiere EP-02 y EP-03 completadas.

### EP-06: Visualización de Rutas
Mapa interactivo con Leaflet + OpenStreetMap que muestra rutas, puntos de entrega y niveles de congestión en el distrito de Huancayo. Requiere EP-05 completada.

### EP-07: Sostenibilidad
Dashboard de indicadores de CO₂, reportes PDF descargables y plan de compensación de carbono con proyectos de reforestación de la región Junín. Requiere EP-05 y EP-06 completadas.

---

## 3. Historias de Usuario

---

### EP-01: Seguridad y Acceso

---

**HU-001**

| Campo | Detalle |
|---|---|
| **ID** | HU-001 |
| **Título** | Iniciar sesión en el sistema |
| **Épica** | EP-01 Seguridad y Acceso |
| **RF Origen** | RF-011: Autenticación y Control de Acceso |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como usuario del sistema,
quiero iniciar sesión con mi correo electrónico y contraseña,
para acceder a los módulos correspondientes a mi rol en RouteZero.

**Criterios de Aceptación:**

Escenario 1: Inicio de sesión exitoso
```gherkin
Dado que un usuario registrado accede a la pantalla de inicio de sesión
Cuando ingresa su correo electrónico y contraseña válidos
Entonces el sistema autentica al usuario, genera un token de sesión seguro y redirige al módulo correspondiente según su rol (Administrador, Operador o Conductor)
```

Escenario 2: Bloqueo por intentos fallidos
```gherkin
Dado que un usuario intenta iniciar sesión
Cuando ingresa credenciales incorrectas 3 veces consecutivas
Entonces el sistema bloquea la cuenta por 15 minutos, registra el evento de seguridad y muestra un mensaje indicando el tiempo de bloqueo restante
```

---

**HU-002**

| Campo | Detalle |
|---|---|
| **ID** | HU-002 |
| **Título** | Acceder solo a módulos permitidos por rol |
| **Épica** | EP-01 Seguridad y Acceso |
| **RF Origen** | RF-011: Autenticación y Control de Acceso |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como usuario autenticado,
quiero que el sistema me permita acceder únicamente a los módulos de mi rol,
para garantizar la seguridad y confidencialidad de la información de Andina Reparto S.A.C.

**Criterios de Aceptación:**

Escenario 1: Acceso denegado a módulo restringido
```gherkin
Dado que un usuario autenticado intenta acceder a un módulo restringido
Cuando su rol no tiene permisos para ese módulo
Entonces el sistema deniega el acceso, redirige al dashboard de su rol y muestra un mensaje informando que no tiene permisos suficientes
```

Escenario 2: Acceso permitido a módulo propio
```gherkin
Dado que el conductor está autenticado
Cuando accede al módulo de visualización de su ruta asignada
Entonces el sistema muestra la ruta y entregas pendientes correctamente
```

---

### EP-02: Gestión de Flota

---

**HU-003**

| Campo | Detalle |
|---|---|
| **ID** | HU-003 |
| **Título** | Registrar vehículo en la flota |
| **Épica** | EP-02 Gestión de Flota |
| **RF Origen** | RF-001: Gestión de Flota de Vehículos |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero registrar un vehículo con sus datos técnicos en el sistema,
para gestionar la flota disponible de Andina Reparto S.A.C.

**Criterios de Aceptación:**

Escenario 1: Registro exitoso de vehículo
```gherkin
Dado que el administrador está autenticado y accede al módulo de gestión de flota
Cuando ingresa todos los datos válidos del vehículo y confirma el registro
Entonces el sistema almacena el vehículo, lo muestra en el listado de flota y confirma el registro exitoso
```

Escenario 2: Placa duplicada
```gherkin
Dado que el administrador intenta registrar un vehículo
Cuando ingresa una placa que ya existe en el sistema
Entonces el sistema rechaza el registro, mantiene el estado previo y muestra un mensaje de error explícito indicando el campo inválido
```

---

**HU-004**

| Campo | Detalle |
|---|---|
| **ID** | HU-004 |
| **Título** | Editar datos de un vehículo registrado |
| **Épica** | EP-02 Gestión de Flota |
| **RF Origen** | RF-001: Gestión de Flota de Vehículos |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como administrador de operaciones,
quiero editar los datos técnicos de un vehículo ya registrado,
para mantener la información de la flota actualizada y precisa.

**Criterios de Aceptación:**

Escenario 1: Edición exitosa
```gherkin
Dado que el administrador está autenticado y accede al módulo de gestión de flota
Cuando edita los datos de un vehículo existente con información actualizada válida
Entonces el sistema actualiza los datos del vehículo y refleja los cambios en tiempo real
```

Escenario 2: Campos obligatorios vacíos
```gherkin
Dado que el administrador edita un vehículo
Cuando deja un campo obligatorio vacío y confirma los cambios
Entonces el sistema rechaza el registro, mantiene el estado previo y muestra un mensaje de error explícito indicando el campo inválido
```

---

**HU-005**

| Campo | Detalle |
|---|---|
| **ID** | HU-005 |
| **Título** | Consultar disponibilidad de la flota |
| **Épica** | EP-02 Gestión de Flota |
| **RF Origen** | RF-001: Gestión de Flota de Vehículos |
| **Story Points** | 2 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero consultar el estado de disponibilidad de cada vehículo de la flota,
para asignar correctamente los vehículos a las rutas del día.

**Criterios de Aceptación:**

Escenario 1: Consulta exitosa
```gherkin
Dado que el administrador está autenticado y accede al módulo de gestión de flota
Cuando filtra los vehículos por estado disponible
Entonces el sistema muestra únicamente los vehículos disponibles para la jornada
```

Escenario 2: Sin vehículos disponibles
```gherkin
Dado que el administrador consulta la disponibilidad de la flota
Cuando todos los vehículos están en ruta o en mantenimiento
Entonces el sistema muestra un mensaje indicando que no hay vehículos disponibles para la jornada
```

---

### EP-03: Gestión de Pedidos

---

**HU-006**

| Campo | Detalle |
|---|---|
| **ID** | HU-006 |
| **Título** | Registrar pedido con coordenadas GPS y ventana de tiempo |
| **Épica** | EP-03 Gestión de Pedidos |
| **RF Origen** | RF-002: Gestión de Pedidos |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como operador de despacho,
quiero registrar un pedido con dirección, coordenadas GPS, peso y ventana de tiempo,
para que el algoritmo pueda incluirlo en la optimización de rutas del distrito de Huancayo.

**Criterios de Aceptación:**

Escenario 1: Registro exitoso con coordenadas válidas
```gherkin
Dado que el operador está autenticado y accede al módulo de pedidos
Cuando registra un pedido con ID de cliente, dirección de entrega en el distrito de Huancayo, coordenadas GPS, peso (kg), ventana de tiempo (hora inicio-fin) y prioridad válidos
Entonces el sistema almacena el pedido, lo asigna al backlog de entregas pendientes y confirma el registro exitoso
```

Escenario 2: Coordenadas fuera de zona de cobertura
```gherkin
Dado que el operador intenta registrar un pedido
Cuando las coordenadas GPS están fuera del área operativa del distrito de Huancayo
Entonces el sistema rechaza el pedido, mantiene el estado previo y muestra un mensaje indicando que la dirección está fuera de la zona de cobertura
```

---

**HU-007**

| Campo | Detalle |
|---|---|
| **ID** | HU-007 |
| **Título** | Registrar pedido con punto de referencia |
| **Épica** | EP-03 Gestión de Pedidos |
| **RF Origen** | RF-002: Gestión de Pedidos |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como operador de despacho,
quiero registrar un pedido usando un punto de referencia cuando la dirección no tiene nomenclatura estándar,
para gestionar entregas en zonas del distrito de Huancayo sin numeración formal.

**Criterios de Aceptación:**

Escenario 1: Registro exitoso con punto de referencia
```gherkin
Dado que el operador está autenticado y registra un pedido
Cuando la dirección no tiene nomenclatura estándar y usa un punto de referencia (ej. "frente al Mercado Modelo, Huancayo")
Entonces el sistema acepta el punto de referencia, lo georreferencia en el mapa y lo almacena correctamente
```

Escenario 2: Sin dirección ni referencia
```gherkin
Dado que el operador registra un pedido
Cuando intenta guardar sin completar la dirección ni el punto de referencia
Entonces el sistema rechaza el registro y muestra un error indicando que se requiere al menos uno de los dos campos
```

---

**HU-008**

| Campo | Detalle |
|---|---|
| **ID** | HU-008 |
| **Título** | Cancelar pedido pendiente |
| **Épica** | EP-03 Gestión de Pedidos |
| **RF Origen** | RF-002: Gestión de Pedidos |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como operador de despacho,
quiero cancelar un pedido que aún no ha sido asignado a una ruta,
para mantener el backlog de entregas actualizado ante cambios del cliente.

**Criterios de Aceptación:**

Escenario 1: Cancelación exitosa
```gherkin
Dado que el operador accede a un pedido en estado PENDIENTE
Cuando selecciona la opción cancelar y confirma la acción
Entonces el sistema cambia el estado del pedido a CANCELADO y lo excluye del backlog de entregas
```

Escenario 2: Pedido ya asignado a ruta
```gherkin
Dado que el operador intenta cancelar un pedido
Cuando el pedido ya está en estado ASIGNADO o EN_CAMINO
Entonces el sistema rechaza la cancelación y muestra un mensaje indicando que debe re-optimizar la ruta
```
---

### EP-04: Gestión de Personas

---

**HU-009**

| Campo | Detalle |
|---|---|
| **ID** | HU-009 |
| **Título** | Registrar conductor |
| **Épica** | EP-04 Gestión de Personas |
| **RF Origen** | RF-008: Gestión de Conductores |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero registrar un conductor con sus datos personales y disponibilidad horaria,
para asignarlo a las rutas respetando la jornada máxima de 8 horas según la Ley N° 30224.

**Criterios de Aceptación:**

Escenario 1: Registro exitoso de conductor
```gherkin
Dado que el administrador está autenticado y accede al módulo de gestión de conductores
Cuando registra un conductor con nombre, DNI, categoría de licencia, disponibilidad horaria y número de contacto válidos
Entonces el sistema almacena el conductor, lo asocia a la flota disponible y confirma el registro exitoso
```

Escenario 2: DNI duplicado
```gherkin
Dado que el administrador intenta registrar un conductor
Cuando ingresa un DNI duplicado o deja campos obligatorios vacíos
Entonces el sistema rechaza el registro y muestra un mensaje de error indicando el campo inválido
```

---

**HU-010**

| Campo | Detalle |
|---|---|
| **ID** | HU-010 |
| **Título** | Registrar cliente con preferencias de entrega |
| **Épica** | EP-04 Gestión de Personas |
| **RF Origen** | RF-009: Módulo de Gestión de Clientes |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como operador de despacho,
quiero registrar un cliente con su tipo de negocio y horario de atención,
para que el sistema considere sus ventanas de tiempo en la optimización de rutas.

**Criterios de Aceptación:**

Escenario 1: Registro exitoso de cliente
```gherkin
Dado que el operador está autenticado y accede al módulo de clientes
Cuando registra un cliente con nombre, tipo de negocio (bodega, restaurante, mercado), horarios preferidos de entrega y punto de referencia en el distrito de Huancayo
Entonces el sistema almacena el perfil del cliente y lo asocia a los pedidos futuros
```

Escenario 2: Nombre duplicado o campos vacíos
```gherkin
Dado que el operador intenta registrar un cliente
Cuando ingresa un nombre duplicado o deja campos obligatorios vacíos
Entonces el sistema rechaza el registro y muestra un mensaje de error indicando el campo inválido
```

---

### EP-05: Optimización de Rutas

---

**HU-011**

| Campo | Detalle |
|---|---|
| **ID** | HU-011 |
| **Título** | Generar rutas optimizadas para la jornada |
| **Épica** | EP-05 Optimización de Rutas |
| **RF Origen** | RF-003: Generación de Rutas Optimizadas |
| **Story Points** | 13 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero generar rutas optimizadas para todos los pedidos del día,
para minimizar la distancia recorrida, el consumo de combustible y las emisiones de CO₂ de la flota de Andina Reparto S.A.C.

**Criterios de Aceptación:**

Escenario 1: Generación exitosa de rutas
```gherkin
Dado que el administrador está autenticado y existen pedidos y vehículos registrados
Cuando solicita la generación de rutas optimizadas para la jornada
Entonces el sistema ejecuta el algoritmo metaheurístico (VRPTW + Green VRP) y retorna rutas válidas en ≤ 45 segundos minimizando distancia, combustible, emisiones de CO₂ y penalizaciones por entregas tardías
```

Escenario 2: Sin vehículos disponibles
```gherkin
Dado que el administrador solicita rutas optimizadas
Cuando no hay vehículos disponibles o la capacidad total de la flota es insuficiente para los pedidos registrados
Entonces el sistema informa la imposibilidad de generar rutas, lista los pedidos sin cobertura y sugiere acciones correctivas
```

---

**HU-012**

| Campo | Detalle |
|---|---|
| **ID** | HU-012 |
| **Título** | Re-optimizar rutas ante evento de cambio operativo |
| **Épica** | EP-05 Optimización de Rutas |
| **RF Origen** | RF-007: Re-optimización Dinámica de Rutas |
| **Story Points** | 8 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero re-optimizar las rutas activas cuando se registra un nuevo pedido, cancelación o incidente de tráfico,
para mantener el cumplimiento de las ventanas de tiempo de entrega en el distrito de Huancayo.

**Criterios de Aceptación:**

Escenario 1: Re-optimización exitosa ante nuevo pedido urgente
```gherkin
Dado que existen rutas activas en ejecución y el administrador registra un nuevo pedido urgente
Cuando solicita la re-optimización de rutas
Entonces el sistema recalcula las rutas afectadas en ≤ 30 segundos integrando el nuevo pedido sin alterar las entregas ya completadas
```

Escenario 2: Sin rutas activas para re-optimizar
```gherkin
Dado que el administrador solicita re-optimización
Cuando no existe ninguna ruta activa en ejecución
Entonces el sistema informa que no hay rutas activas para re-optimizar y sugiere generar nuevas rutas desde el módulo correspondiente
```

---

### EP-06: Visualización de Rutas

---

**HU-013**

| Campo | Detalle |
|---|---|
| **ID** | HU-013 |
| **Título** | Visualizar rutas optimizadas en mapa interactivo |
| **Épica** | EP-06 Visualización de Rutas |
| **RF Origen** | RF-004: Visualización de Rutas en Mapa Interactivo |
| **Story Points** | 5 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero visualizar las rutas optimizadas en un mapa interactivo del distrito de Huancayo,
para monitorear el estado de las entregas en tiempo real.

**Criterios de Aceptación:**

Escenario 1: Visualización exitosa de rutas
```gherkin
Dado que existen rutas optimizadas generadas y el usuario accede al módulo de mapa
Cuando visualiza el mapa interactivo con Leaflet + OpenStreetMap
Entonces el sistema muestra el trazado de cada ruta, los puntos de entrega, el tiempo estimado por tramo y el nivel de congestión (verde/amarillo/rojo) en las vías del distrito de Huancayo
```

Escenario 2: Sin rutas generadas para la jornada
```gherkin
Dado que el usuario accede al módulo de mapa
Cuando no hay rutas generadas para la jornada actual
Entonces el sistema muestra el mapa base del distrito de Huancayo sin rutas y despliega un mensaje indicando que no hay rutas disponibles
```

---

**HU-014**

| Campo | Detalle |
|---|---|
| **ID** | HU-014 |
| **Título** | Visualizar ruta asignada en modo conductor |
| **Épica** | EP-06 Visualización de Rutas |
| **RF Origen** | RF-004: Visualización de Rutas en Mapa Interactivo |
| **Story Points** | 3 |
| **Prioridad** | Alta |

**Redacción:**
Como conductor de reparto,
quiero ver mi ruta asignada en el mapa con las entregas pendientes y alertas de tráfico,
para completar mi jornada de forma eficiente y segura en el distrito de Huancayo.

**Criterios de Aceptación:**

Escenario 1: Acceso exitoso al modo conductor
```gherkin
Dado que el conductor accede al mapa en modo conductor
Cuando selecciona su ruta asignada
Entonces el sistema muestra únicamente su ruta, los puntos de entrega pendientes y las alertas de tráfico relevantes en un formato simplificado
```

Escenario 2: Sin ruta asignada
```gherkin
Dado que el conductor accede al modo conductor
Cuando no tiene ninguna ruta asignada para la jornada
Entonces el sistema muestra un mensaje indicando que no tiene rutas asignadas por el momento
```

---

### EP-07: Sostenibilidad

---

**HU-015**

| Campo | Detalle |
|---|---|
| **ID** | HU-015 |
| **Título** | Visualizar dashboard de indicadores de sostenibilidad |
| **Épica** | EP-07 Sostenibilidad |
| **RF Origen** | RF-005: Dashboard de Indicadores de Sostenibilidad |
| **Story Points** | 5 |
| **Prioridad** | Alta |

**Redacción:**
Como administrador de operaciones,
quiero visualizar en tiempo real las métricas de CO₂, combustible ahorrado y cumplimiento de entregas,
para tomar decisiones operativas basadas en datos de sostenibilidad.

**Criterios de Aceptación:**

Escenario 1: Dashboard con datos disponibles
```gherkin
Dado que el administrador está autenticado y accede al dashboard
Cuando hay jornadas operativas registradas con rutas ejecutadas
Entonces el sistema muestra en tiempo real: distancia total recorrida (km), emisiones de CO₂ (kg), combustible ahorrado (L), cumplimiento de ventanas de tiempo (%) y ahorro económico en soles (S/)
```

Escenario 2: Sin datos del periodo seleccionado
```gherkin
Dado que el administrador accede al dashboard
Cuando no hay jornadas operativas registradas en el periodo seleccionado
Entonces el sistema muestra el dashboard con valores en cero y un mensaje indicando que no hay datos disponibles para el periodo
```

---

**HU-016**

| Campo | Detalle |
|---|---|
| **ID** | HU-016 |
| **Título** | Descargar reporte de sostenibilidad en PDF |
| **Épica** | EP-07 Sostenibilidad |
| **RF Origen** | RF-006: Generación de Reportes de Sostenibilidad |
| **Story Points** | 5 |
| **Prioridad** | Media |

**Redacción:**
Como gerente general,
quiero descargar un reporte PDF con las métricas de CO₂ y costos operativos del periodo,
para evaluar el impacto ambiental y económico de la operación de Andina Reparto S.A.C.

**Criterios de Aceptación:**

Escenario 1: Descarga exitosa del reporte
```gherkin
Dado que el administrador está autenticado y accede al módulo de reportes
Cuando selecciona el periodo y solicita generar el reporte
Entonces el sistema genera un PDF descargable con: resumen de emisiones de CO₂ por ruta, costo del ciclo de vida de la flota, ahorro en combustible y cumplimiento de metas de sostenibilidad
```

Escenario 2: Sin datos para el periodo seleccionado
```gherkin
Dado que el administrador solicita generar un reporte
Cuando no hay datos operativos registrados para el periodo seleccionado
Entonces el sistema informa que no hay datos suficientes para generar el reporte y sugiere seleccionar otro periodo
```

---

**HU-017**

| Campo | Detalle |
|---|---|
| **ID** | HU-017 |
| **Título** | Consultar plan de compensación de carbono |
| **Épica** | EP-07 Sostenibilidad |
| **RF Origen** | RF-010: Plan de Compensación de Carbono |
| **Story Points** | 3 |
| **Prioridad** | Baja |

**Redacción:**
Como administrador de operaciones,
quiero consultar el plan de compensación de carbono con la cantidad de árboles necesarios,
para gestionar alianzas con proyectos de reforestación de la región Junín.

**Criterios de Aceptación:**

Escenario 1: Plan generado exitosamente
```gherkin
Dado que el administrador está autenticado y accede al módulo de sostenibilidad
Cuando solicita el cálculo del plan de compensación de carbono para el periodo seleccionado
Entonces el sistema calcula el CO₂ total emitido por la flota, determina la cantidad de árboles necesarios para compensar las emisiones y propone alianzas con proyectos de reforestación de la región Junín
```

Escenario 2: Sin datos de emisiones registrados
```gherkin
Dado que el administrador solicita el plan de compensación
Cuando no hay datos de emisiones registrados para el periodo seleccionado
Entonces el sistema informa que no hay datos suficientes y sugiere ejecutar al menos una jornada operativa antes de generar el plan
```

---

## 4. Historias Técnicas

---

### EP-01: Seguridad y Acceso

---

**HT-01**

| Campo | Detalle |
|---|---|
| **ID** | HT-01 |
| **Título** | Implementar autenticación JWT y protección OWASP Top 10 |
| **Épica** | EP-01 Seguridad y Acceso |
| **Tipo** | Seguridad |
| **RNF Origen** | RNF-003: Seguridad — Intento de inyección SQL en endpoint de autenticación / RNF-004: Seguridad — Intento de acceso a módulo restringido sin permisos |
| **Story Points** | 8 |
| **Prioridad** | Alta |

**Redacción:**
Como equipo de desarrollo,
quiero implementar autenticación basada en JWT y las medidas de seguridad OWASP Top 10,
para proteger los datos de conductores y clientes cumpliendo la Ley N° 29733.

**Criterios de Aceptación:**

Escenario 1: Protección contra inyección SQL
```gherkin
Dado que un atacante intenta una inyección SQL en el endpoint de autenticación
Cuando el sistema recibe la petición maliciosa
Entonces la bloquea, registra el evento de auditoría y retorna HTTP 400 con 0% de vulnerabilidades críticas OWASP Top 10 ejecutables
```

Escenario 2: Control de acceso por rol
```gherkin
Dado que un usuario no autorizado intenta acceder a un módulo restringido
Cuando el sistema valida los permisos del token JWT
Entonces deniega el acceso, redirige al dashboard del rol y registra el intento con 100% de intentos bloqueados
```

---

**HT-02**

| Campo | Detalle |
|---|---|
| **ID** | HT-02 |
| **Título** | Implementar cifrado de datos y cumplimiento Ley N° 29733 |
| **Épica** | EP-01 Seguridad y Acceso |
| **Tipo** | Seguridad / Normativa |
| **RNF Origen** | RNF-013: Seguridad de datos — El sistema debe cumplir con la Ley N° 29733 (Protección de Datos Personales del Perú) |
| **Story Points** | 5 |
| **Prioridad** | Alta |

**Redacción:**
Como equipo de desarrollo,
quiero implementar cifrado en reposo para datos personales y cumplir la Ley N° 29733,
para proteger el 100% de los datos de conductores y clientes almacenados en PostgreSQL.

**Criterios de Aceptación:**

Escenario 1: Datos personales cifrados en reposo
```gherkin
Dado que el sistema almacena datos personales de conductores y clientes
Cuando se persisten en la base de datos PostgreSQL
Entonces el 100% de los datos personales están almacenados con cifrado en reposo cumpliendo la Ley N° 29733
```

Escenario 2: Consentimiento explícito registrado
```gherkin
Dado que un nuevo conductor o cliente es registrado en el sistema
Cuando el operador completa el formulario de registro
Entonces el sistema registra el consentimiento explícito del titular antes de almacenar sus datos personales
```

---

**HT-03**

| Campo | Detalle |
|---|---|
| **ID** | HT-03 |
| **Título** | Configurar infraestructura de despliegue en Render y Vercel |
| **Épica** | EP-01 Seguridad y Acceso |
| **Tipo** | Infraestructura / DevOps |
| **RNF Origen** | RNF-005: Disponibilidad — Caída del servicio de despliegue en horario operativo (5:00 AM – 10:00 PM) |
| **Story Points** | 5 |
| **Prioridad** | Alta |

**Redacción:**
Como equipo de desarrollo,
quiero configurar el despliegue automático del backend en Render y el frontend en Vercel,
para garantizar una disponibilidad ≥ 99.5% en horario operativo con URLs públicas estables para la sustentación.

**Criterios de Aceptación:**

Escenario 1: Despliegue exitoso ante push a main
```gherkin
Dado que el equipo realiza un push a la rama main
Cuando Render y Vercel detectan el cambio en el repositorio
Entonces despliegan automáticamente el backend FastAPI y el frontend React.js con URLs públicas accesibles
```

Escenario 2: Recuperación ante caída del servicio
```gherkin
Dado que el servicio de despliegue experimenta una caída
Cuando el sistema detecta la indisponibilidad
Entonces se recupera automáticamente garantizando disponibilidad ≥ 99.5% en horario operativo (5:00 AM – 10:00 PM)
```

---

### EP-02: Gestión de Flota

---

**HT-04**

| Campo | Detalle |
|---|---|
| **ID** | HT-04 |
| **Título** | Pruebas unitarias del módulo de flota |
| **Épica** | EP-02 Gestión de Flota |
| **Tipo** | Calidad / Testing |
| **RNF Origen** | DoD criterio 1 — Cobertura de pruebas unitarias ≥ 80% |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar pruebas unitarias para el módulo de gestión de flota,
para garantizar una cobertura ≥ 80% conforme al Definition of Done del proyecto.

**Criterios de Aceptación:**

Escenario 1: Cobertura alcanzada
```gherkin
Dado que el módulo de flota está implementado
Cuando se ejecuta pytest-cov sobre los endpoints de flota
Entonces la cobertura de pruebas unitarias es ≥ 80% sin errores críticos
```

Escenario 2: Prueba de registro con placa duplicada
```gherkin
Dado que el módulo de flota está en ambiente de pruebas
Cuando se ejecuta el caso de prueba de registro con placa duplicada
Entonces el sistema retorna el error esperado y la cobertura del caso queda registrada
```

---

### EP-03: Gestión de Pedidos

---

**HT-05**

| Campo | Detalle |
|---|---|
| **ID** | HT-05 |
| **Título** | Pruebas unitarias del módulo de pedidos |
| **Épica** | EP-03 Gestión de Pedidos |
| **Tipo** | Calidad / Testing |
| **RNF Origen** | DoD criterio 1 — Cobertura de pruebas unitarias ≥ 80% |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar pruebas unitarias para el módulo de gestión de pedidos,
para garantizar una cobertura ≥ 80% conforme al Definition of Done del proyecto.

**Criterios de Aceptación:**

Escenario 1: Cobertura alcanzada
```gherkin
Dado que el módulo de pedidos está implementado
Cuando se ejecuta pytest-cov sobre los endpoints de pedidos
Entonces la cobertura de pruebas unitarias es ≥ 80% sin errores críticos
```

Escenario 2: Prueba de coordenadas fuera de zona
```gherkin
Dado que el módulo de pedidos está en ambiente de pruebas
Cuando se ejecuta el caso de prueba con coordenadas fuera del distrito de Huancayo
Entonces el sistema retorna el error esperado y la cobertura del caso queda registrada
```

---

### EP-04: Gestión de Personas

---

**HT-06**

| Campo | Detalle |
|---|---|
| **ID** | HT-06 |
| **Título** | Pruebas unitarias del módulo de personas |
| **Épica** | EP-04 Gestión de Personas |
| **Tipo** | Calidad / Testing |
| **RNF Origen** | DoD criterio 1 — Cobertura de pruebas unitarias ≥ 80% |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar pruebas unitarias para el módulo de gestión de conductores y clientes,
para garantizar una cobertura ≥ 80% conforme al Definition of Done del proyecto.

**Criterios de Aceptación:**

Escenario 1: Cobertura alcanzada
```gherkin
Dado que el módulo de personas está implementado
Cuando se ejecuta pytest-cov sobre los endpoints de conductores y clientes
Entonces la cobertura de pruebas unitarias es ≥ 80% sin errores críticos
```

Escenario 2: Prueba de DNI duplicado
```gherkin
Dado que el módulo de personas está en ambiente de pruebas
Cuando se ejecuta el caso de prueba de registro con DNI duplicado
Entonces el sistema retorna el error esperado y la cobertura del caso queda registrada
```

---

### EP-05: Optimización de Rutas

---

**HT-07**

| Campo | Detalle |
|---|---|
| **ID** | HT-07 |
| **Título** | Implementar motor de optimización ACO para VRPTW + Green VRP |
| **Épica** | EP-05 Optimización de Rutas |
| **Tipo** | Rendimiento |
| **RNF Origen** | RNF-001: Rendimiento — Solicitud de generación de rutas optimizadas para 150 pedidos y 15 vehículos / RNF-002: Rendimiento — Solicitud de re-optimización dinámica ante incidente de tráfico en Av. Ferrocarril |
| **Story Points** | 13 |
| **Prioridad** | Alta |

**Redacción:**
Como equipo de desarrollo,
quiero implementar el algoritmo ACO (Colonia de Hormigas) para VRPTW + Green VRP,
para que el sistema genere rutas optimizadas en ≤ 45 segundos y re-optimice en ≤ 30 segundos.

**Criterios de Aceptación:**

Escenario 1: Rendimiento dentro del umbral para generación
```gherkin
Dado que el motor ACO recibe 150 pedidos y 15 vehículos como entrada
Cuando se ejecuta el algoritmo de optimización
Entonces retorna rutas válidas en ≤ 45 segundos en el percentil 95 (P95) respetando capacidades y ventanas de tiempo
```

Escenario 2: Rendimiento dentro del umbral para re-optimización
```gherkin
Dado que el motor ACO recibe una solicitud de re-optimización con rutas activas
Cuando se detecta un incidente de tráfico en Av. Ferrocarril
Entonces recalcula las rutas afectadas en ≤ 30 segundos en el percentil 95 (P95)
```

---

**HT-08**

| Campo | Detalle |
|---|---|
| **ID** | HT-08 |
| **Título** | Diseñar arquitectura escalable para 1,000 pedidos diarios |
| **Épica** | EP-05 Optimización de Rutas |
| **Tipo** | Arquitectura |
| **RNF Origen** | RNF-008: Escalabilidad — Incremento de pedidos diarios de 150 a 1,000 con operación a carga máxima |
| **Story Points** | 8 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero diseñar una arquitectura escalable por características con patrón Repository,
para que el sistema maneje hasta 1,000 pedidos diarios con tiempo de respuesta ≤ 2 segundos.

**Criterios de Aceptación:**

Escenario 1: Respuesta dentro del umbral con carga máxima
```gherkin
Dado que el sistema opera con 1,000 pedidos concurrentes
Cuando el backend procesa las solicitudes con la arquitectura por características
Entonces el tiempo de respuesta de la API es ≤ 2 segundos sin degradación del servicio
```

Escenario 2: Separación de responsabilidades verificada
```gherkin
Dado que el desarrollador revisa la estructura del código fuente
Cuando analiza la organización de módulos del backend
Entonces cada módulo (flota, pedidos, rutas, algoritmo, dashboard) es independiente y no tiene dependencias cruzadas directas
```

---

### EP-06: Visualización de Rutas

---

**HT-09**

| Campo | Detalle |
|---|---|
| **ID** | HT-09 |
| **Título** | Implementar diseño responsive y cumplimiento WCAG 2.1 AA |
| **Épica** | EP-06 Visualización de Rutas |
| **Tipo** | Accesibilidad / Frontend |
| **RNF Origen** | RNF-006: Usabilidad — Acceso al módulo de rutas en modo conductor desde dispositivo móvil / RNF-007: Accesibilidad — Acceso a cualquier módulo del sistema por usuario con discapacidad visual parcial |
| **Story Points** | 5 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar un diseño responsive accesible bajo WCAG 2.1 nivel AA,
para garantizar que conductores con dispositivos móviles básicos y usuarios con discapacidad visual puedan usar el sistema sin dificultad.

**Criterios de Aceptación:**

Escenario 1: Conductor completa tarea en ≤ 3 pasos
```gherkin
Dado que el conductor accede al módulo de rutas en modo conductor desde un dispositivo móvil
Cuando navega por las entregas pendientes de su jornada
Entonces completa la tarea principal en ≤ 3 pasos sin asistencia externa
```

Escenario 2: Score de accesibilidad Lighthouse ≥ 90
```gherkin
Dado que el frontend está desplegado en Vercel
Cuando se ejecuta una auditoría con Google Lighthouse
Entonces el score de accesibilidad es ≥ 90 cumpliendo WCAG 2.1 nivel AA con contraste y etiquetas ARIA correctas
```

---

**HT-10**

| Campo | Detalle |
|---|---|
| **ID** | HT-10 |
| **Título** | Pruebas de integración del mapa interactivo |
| **Épica** | EP-06 Visualización de Rutas |
| **Tipo** | Calidad / Testing |
| **RNF Origen** | DoD criterio 1 — Cobertura de pruebas unitarias ≥ 80% |
| **Story Points** | 3 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar pruebas de integración para el módulo de visualización de rutas en mapa,
para verificar que Leaflet + OpenStreetMap renderizan correctamente las rutas optimizadas del distrito de Huancayo.

**Criterios de Aceptación:**

Escenario 1: Mapa renderiza rutas correctamente
```gherkin
Dado que existen rutas optimizadas generadas en el sistema
Cuando se ejecuta la prueba de integración del módulo de mapa
Entonces Leaflet renderiza el trazado de rutas, puntos de entrega y niveles de congestión sin errores
```

Escenario 2: Mapa sin rutas disponibles
```gherkin
Dado que no hay rutas generadas para la jornada
Cuando se ejecuta la prueba de integración del módulo de mapa
Entonces el sistema muestra el mapa base del distrito de Huancayo sin errores de renderizado
```

---

### EP-07: Sostenibilidad

---

**HT-11**

| Campo | Detalle |
|---|---|
| **ID** | HT-11 |
| **Título** | Optimizar consultas SQL aplicando principios Green Software |
| **Épica** | EP-07 Sostenibilidad |
| **Tipo** | Rendimiento / Sostenibilidad |
| **RNF Origen** | RNF-011: Eficiencia energética — Ejecución de consultas SQL durante la generación de rutas con reducción de ciclos de CPU |
| **Story Points** | 3 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero optimizar las consultas SQL y aplicar principios Green Software en el backend,
para que las consultas críticas se ejecuten en ≤ 500ms reduciendo el consumo de CPU y RAM.

**Criterios de Aceptación:**

Escenario 1: Consultas críticas dentro del umbral
```gherkin
Dado que el sistema ejecuta una consulta de generación de rutas con 150 pedidos
Cuando la consulta accede a la base de datos PostgreSQL
Entonces se ejecuta en ≤ 500ms con índices aplicados en todas las tablas de consulta frecuente
```

Escenario 2: Sin full table scans en producción
```gherkin
Dado que el administrador de base de datos verifica el plan de ejecución
Cuando analiza las consultas más frecuentes del sistema en producción
Entonces no hay full table scans y todas las tablas críticas tienen índices aplicados
```

---

**HT-12**

| Campo | Detalle |
|---|---|
| **ID** | HT-12 |
| **Título** | Pruebas de generación de reportes PDF |
| **Épica** | EP-07 Sostenibilidad |
| **Tipo** | Calidad / Testing |
| **RNF Origen** | DoD criterio 1 — Cobertura de pruebas unitarias ≥ 80% |
| **Story Points** | 2 |
| **Prioridad** | Media |

**Redacción:**
Como equipo de desarrollo,
quiero implementar pruebas para el módulo de generación de reportes PDF de sostenibilidad,
para verificar que los reportes se generan correctamente con las métricas de CO₂ y costos operativos.

**Criterios de Aceptación:**

Escenario 1: Reporte generado correctamente
```gherkin
Dado que existen datos operativos registrados en el sistema
Cuando se ejecuta la prueba del módulo de reportes PDF
Entonces el sistema genera un PDF válido con emisiones CO₂, ahorro en combustible y costos operativos sin errores
```

Escenario 2: Sin datos para el periodo
```gherkin
Dado que no hay datos operativos para el periodo seleccionado
Cuando se ejecuta la prueba del módulo de reportes
Entonces el sistema retorna el mensaje de error esperado sin generar un PDF vacío
```

---

## 5. Definition of Done (DoD) Global del Proyecto

El siguiente conjunto de criterios define cuándo una Historia de Usuario o Historia Técnica se considera **finalizada ("Done")** en el proyecto RouteZero:

| # | Criterio | Métrica Objetiva |
|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80% medida con pytest-cov (backend) y Jest (frontend) |
| 2 | Análisis estático de código | 0 vulnerabilidades críticas detectadas por CodeQL o SonarQube |
| 3 | Revisión de código (Peer Review) | Al menos 1 Pull Request aprobado por un par técnico antes del merge a main |
| 4 | Despliegue en ambiente de Staging | Build exitoso en Render (backend) y Vercel (frontend) sin errores de compilación |
| 5 | Documentación de API actualizada | Todos los endpoints de la historia documentados en Swagger/OpenAPI en `/docs` |
| 6 | Criterios de Aceptación verificados | Todos los escenarios Gherkin de la historia ejecutados y aprobados |
| 7 | Cumplimiento de estándares | Sin errores W3C, score Lighthouse ≥ 90, sin vulnerabilidades OWASP críticas |
| 8 | Commit en rama del integrante | Historia commiteada en rama propia e integrada via Pull Request a main |

---

## 6. Tabla de Trazabilidad

| HU/HT | Título | RF/RNF Origen | Épica |
|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema | RF-011: Autenticación y Control de Acceso | EP-01 |
| HU-002 | Acceder solo a módulos permitidos por rol | RF-011: Autenticación y Control de Acceso | EP-01 |
| HU-003 | Registrar vehículo en la flota | RF-001: Gestión de Flota de Vehículos | EP-02 |
| HU-004 | Editar datos de un vehículo registrado | RF-001: Gestión de Flota de Vehículos | EP-02 |
| HU-005 | Consultar disponibilidad de la flota | RF-001: Gestión de Flota de Vehículos | EP-02 |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | RF-002: Gestión de Pedidos | EP-03 |
| HU-007 | Registrar pedido con punto de referencia | RF-002: Gestión de Pedidos | EP-03 |
| HU-008 | Cancelar pedido pendiente | RF-002: Gestión de Pedidos | EP-03 |
| HU-009 | Registrar conductor | RF-008: Gestión de Conductores | EP-04 |
| HU-010 | Registrar cliente con preferencias de entrega | RF-009: Módulo de Gestión de Clientes | EP-04 |
| HU-011 | Generar rutas optimizadas para la jornada | RF-003: Generación de Rutas Optimizadas | EP-05 |
| HU-012 | Re-optimizar rutas ante evento de cambio operativo | RF-007: Re-optimización Dinámica de Rutas | EP-05 |
| HU-013 | Visualizar rutas optimizadas en mapa interactivo | RF-004: Visualización de Rutas en Mapa Interactivo | EP-06 |
| HU-014 | Visualizar ruta asignada en modo conductor | RF-004: Visualización de Rutas en Mapa Interactivo | EP-06 |
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | RF-005: Dashboard de Indicadores de Sostenibilidad | EP-07 |
| HU-016 | Descargar reporte de sostenibilidad en PDF | RF-006: Generación de Reportes de Sostenibilidad | EP-07 |
| HU-017 | Consultar plan de compensación de carbono | RF-010: Plan de Compensación de Carbono | EP-07 |
| HT-01 | Implementar autenticación JWT y OWASP Top 10 | RNF-003, RNF-004: Seguridad | EP-01 |
| HT-02 | Implementar cifrado y cumplimiento Ley N° 29733 | RNF-013: Seguridad de datos | EP-01 |
| HT-03 | Configurar infraestructura Render y Vercel | RNF-005: Disponibilidad | EP-01 |
| HT-04 | Pruebas unitarias del módulo de flota | DoD criterio 1 | EP-02 |
| HT-05 | Pruebas unitarias del módulo de pedidos | DoD criterio 1 | EP-03 |
| HT-06 | Pruebas unitarias del módulo de personas | DoD criterio 1 | EP-04 |
| HT-07 | Implementar motor de optimización ACO | RNF-001, RNF-002: Rendimiento | EP-05 |
| HT-08 | Diseñar arquitectura escalable | RNF-008: Escalabilidad | EP-05 |
| HT-09 | Implementar diseño responsive y WCAG 2.1 AA | RNF-006, RNF-007: Usabilidad y Accesibilidad | EP-06 |
| HT-10 | Pruebas de integración del mapa interactivo | DoD criterio 1 | EP-06 |
| HT-11 | Optimizar consultas SQL con Green Software | RNF-011: Eficiencia energética | EP-07 |
| HT-12 | Pruebas de generación de reportes PDF | DoD criterio 1 | EP-07 |

---

## 7. Resumen del Backlog

| ID | Título | Épica | Tipo | Story Points | Prioridad |
|---|---|---|---|---|---|
| HU-001 | Iniciar sesión en el sistema | EP-01 | HU | 3 | Alta |
| HU-002 | Acceder solo a módulos permitidos por rol | EP-01 | HU | 3 | Alta |
| HU-003 | Registrar vehículo en la flota | EP-02 | HU | 3 | Alta |
| HU-004 | Editar datos de un vehículo registrado | EP-02 | HU | 2 | Media |
| HU-005 | Consultar disponibilidad de la flota | EP-02 | HU | 2 | Alta |
| HU-006 | Registrar pedido con coordenadas GPS y ventana de tiempo | EP-03 | HU | 3 | Alta |
| HU-007 | Registrar pedido con punto de referencia | EP-03 | HU | 2 | Media |
| HU-008 | Cancelar pedido pendiente | EP-03 | HU | 2 | Media |
| HU-009 | Registrar conductor | EP-04 | HU | 3 | Alta |
| HU-010 | Registrar cliente con preferencias de entrega | EP-04 | HU | 2 | Media |
| HU-011 | Generar rutas optimizadas para la jornada | EP-05 | HU | 13 | Alta |
| HU-012 | Re-optimizar rutas ante evento de cambio operativo | EP-05 | HU | 8 | Alta |
| HU-013 | Visualizar rutas optimizadas en mapa interactivo | EP-06 | HU | 5 | Alta |
| HU-014 | Visualizar ruta asignada en modo conductor | EP-06 | HU | 3 | Alta |
| HU-015 | Visualizar dashboard de indicadores de sostenibilidad | EP-07 | HU | 5 | Alta |
| HU-016 | Descargar reporte de sostenibilidad en PDF | EP-07 | HU | 5 | Media |
| HU-017 | Consultar plan de compensación de carbono | EP-07 | HU | 3 | Baja |
| HT-01 | Implementar autenticación JWT y OWASP Top 10 | EP-01 | HT | 8 | Alta |
| HT-02 | Implementar cifrado y cumplimiento Ley N° 29733 | EP-01 | HT | 5 | Alta |
| HT-03 | Configurar infraestructura Render y Vercel | EP-01 | HT | 5 | Alta |
| HT-04 | Pruebas unitarias del módulo de flota | EP-02 | HT | 2 | Media |
| HT-05 | Pruebas unitarias del módulo de pedidos | EP-03 | HT | 2 | Media |
| HT-06 | Pruebas unitarias del módulo de personas | EP-04 | HT | 2 | Media |
| HT-07 | Implementar motor de optimización ACO | EP-05 | HT | 13 | Alta |
| HT-08 | Diseñar arquitectura escalable | EP-05 | HT | 8 | Media |
| HT-09 | Implementar diseño responsive y WCAG 2.1 AA | EP-06 | HT | 5 | Media |
| HT-10 | Pruebas de integración del mapa interactivo | EP-06 | HT | 3 | Media |
| HT-11 | Optimizar consultas SQL con Green Software | EP-07 | HT | 3 | Media |
| HT-12 | Pruebas de generación de reportes PDF | EP-07 | HT | 2 | Media |
| | **TOTAL Story Points** | | | **125** | |

---

[← Volver al README Principal](../../README.md)