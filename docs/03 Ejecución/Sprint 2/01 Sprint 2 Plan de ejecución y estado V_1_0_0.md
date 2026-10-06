# 01 Sprint 2 — Plan de Ejecución y Estado

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Sprint** | Sprint 2 — Personas y Algoritmo ACO (03 oct – 16 oct 2026) |
| **Fecha de corte** | 2026-10-05 |
| **Inspección** | 2026-10-16 |
| **Versión** | 1.0.0 |

[← Volver al README Principal](../../../README.md)

---

## 1. Objetivo del Sprint

Meta definida en el Sprint Planning (ver [`02 Artefactos Jira`](../../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_0_0.md)):

> *Implementar la gestión de conductores y clientes (EP-04) e iniciar el desarrollo del motor de optimización ACO para la generación de rutas VRPTW + Green VRP (EP-05).*

El sprint compromete **6 ítems y 41 Story Points** (3 Historias de Usuario y 3 Historias Técnicas). Este documento registra el estado real de cada ítem a la fecha de corte y el plan para cerrar el sprint antes de la inspección.

## 2. Alcance comprometido y estado al 05-10-2026

Estados: **Completada** (cumple todos sus escenarios de aceptación), **Parcial** (parte del ítem ya existe y está verificada) y **Pendiente** (sin implementación).

| ID | Título | Épica | SP (Jira) | Responsable (Jira) | Estado | Avance verificado | Falta para cerrarla |
|---|---|---|---|---|---|---|---|
| HU-009 | Registrar conductor | EP-04 | 3 | Guerra Lozano Keen | Pendiente | Rol `CONDUCTOR` y vista mobile-first del conductor ya existen (Sprint 1); la tabla `conductores` está diseñada en [`11. Base de datos`](../../01%20Inicio/11.%20Base%20de%20datos%20V_1_4_0.md) | Tabla y política RLS, módulo `conductores/` (alta, DNI único, categoría de licencia, disponibilidad horaria, contacto), consentimiento explícito RN-013, pantalla de gestión |
| HU-010 | Registrar cliente con preferencias de entrega | EP-04 | 2 | Uscuvilca Ramos Abraham Luis | Parcial | Módulo mínimo `clientes/` (registrar y listar) con validación de zona RN-007, referencia en texto libre y selector de ubicación con geocodificación | Tipo de negocio (bodega, restaurante, mercado), horario preferido de entrega, nombre duplicado rechazado, pantalla propia de clientes |
| HU-011 | Generar rutas optimizadas para la jornada | EP-05 | 13 | Inciso Aguilar Elizabeth Antonela | Pendiente | Pedidos, vehículos y zona de cobertura ya disponibles como entrada del motor | Tablas `rutas` y `ruta_pedidos`, endpoint de generación, caso "sin vehículos o capacidad insuficiente" con lista de pedidos sin cobertura, pantalla |
| HT-07 | Implementar motor de optimización ACO (VRPTW + Green VRP) | EP-05 | 2 | Espinoza Tiza Yago Imanol | Pendiente | — | Módulo `algoritmo/` con ACO, matriz de distancias, restricciones de capacidad y ventanas de tiempo, medición de rendimiento (≤ 45 s para 150 pedidos y 15 vehículos, P95) |
| HT-08 | Diseñar arquitectura escalable para 1,000 pedidos diarios | EP-05 | 13 | Inciso Aguilar Elizabeth Antonela | Pendiente | Arquitectura por características con patrón Repository ya aplicada en autenticación, flota, clientes y pedidos | Módulos `rutas/` y `algoritmo/` independientes, índices SQL, prueba de carga con 1,000 pedidos (≤ 2 s por respuesta) |
| HT-06 | Pruebas unitarias del módulo de personas | EP-04 | 8 | Guerra Lozano Keen | Pendiente | Patrón de pruebas con pytest ya establecido (65 pruebas, 95 % de cobertura) | Depende de HU-009 y HU-010; incluir caso de DNI duplicado |

**Resumen del corte:** de los 41 SP comprometidos, ningún ítem está completado; **HU-010 (2 SP) tiene avance parcial** y 39 SP están pendientes.

### 2.1 Diferencias entre Jira y la documentación de planificación

Al confirmar el tablero de Jira contra [`01 Transformando a ágil`](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md) se encontraron **los mismos ítems** en los sprints 2, 3 y 4, pero con Story Points distintos en algunos:

| Ítem | SP en la documentación | SP en Jira | Efecto en el total |
|---|---|---|---|
| HT-06 Pruebas unitarias del módulo de personas | 2 | 8 | Sprint 2: el total sigue en 41 porque las diferencias se compensan |
| HT-07 Motor de optimización ACO | 13 | 2 | |
| HT-08 Arquitectura escalable | 8 | 13 | |
| HT-10 Pruebas de integración del mapa interactivo | 3 | 5 | Sprint 3: 26 SP en Jira frente a 24 en la documentación (el total del proyecto pasaría de 125 a 127) |

El Sprint 4 (HU-015, HU-016, HU-017, HT-11, HT-12; 18 SP) coincide por completo. **Decisión pendiente del equipo:** este documento usa los puntos de Jira por ser el tablero operativo, pero los puntos de HT-06, HT-07, HT-08 y HT-10 deben confirmarse y alinearse en un solo lugar (13 SP parecen más propios del motor ACO que de la arquitectura).

## 3. Trabajo adicional al alcance comprometido

Antes de iniciar los ítems del sprint se atendieron observaciones surgidas de las pruebas del Sprint 1 (ver [`02 Registro de Impedimentos`](Implementaci%C3%B3n/02%20Registro%20de%20Impedimentos%20V_1_0_0.md)):

- **Flota**: el filtro por estado tardaba en responder (cada cambio de filtro hacía un viaje a la base de datos remota); ahora la flota se carga una vez y se filtra en el navegador.
- **Flota**: el registro de vehículos mostraba un mensaje ilegible (`[object Object]`) ante errores de validación; ahora se muestra el campo inválido y su motivo. Además se ajustó la entrada de decimales de los campos numéricos y se normaliza la placa (sin espacios, en mayúsculas).
- **Control de acceso en la interfaz**: la sección "Flota" ya no se muestra al rol Operador (la API ya le respondía 403) y la ruta queda protegida también en el frontend.

## 4. Definition of Done — metas del sprint

Criterios del DoD global ([`01 Transformando a ágil`](../../02%20Planificaci%C3%B3n/01%20Transformando%20a%20%C3%A1gil%20V_1_0_0.md), sección 5), aplicados a lo que entregue este sprint:

| # | Criterio | Meta | Estado |
|---|---|---|---|
| 1 | Cobertura de pruebas unitarias | ≥ 80 % con pytest-cov sobre `conductores/`, `clientes/`, `rutas/` y `algoritmo/` | Pendiente |
| 2 | Análisis estático | 0 vulnerabilidades críticas (Bandit, pip-audit, npm audit) | Pendiente |
| 3 | Revisión de código | Pull Request aprobado antes del merge a `main` | Pendiente |
| 4 | Despliegue en Staging | Build exitoso en Render y Vercel | Pendiente |
| 5 | Documentación de API | Endpoints nuevos documentados en Swagger/OpenAPI | Pendiente |
| 6 | Criterios de aceptación verificados | Escenarios de HU-009, HU-010 y HU-011 ejecutados y aprobados | Pendiente |
| 7 | Cumplimiento de estándares | Lighthouse ≥ 90 (riesgo RSK-007: auditar desde este sprint), sin vulnerabilidades OWASP críticas | Pendiente |
| 8 | Commit en rama e integración por Pull Request | Ramas `backend` y `frontend` integradas a `main` | Pendiente |

## 5. Plan de trabajo (05-10 → 16-10)

Propuesta **sujeta a validación del equipo**. Incorpora las acciones de la retrospectiva del Sprint 1: dueño por módulo y checkpoint de medio sprint.

| Fecha | Foco | Resultado verificable |
|---|---|---|
| 05-10 a 06-10 | Documentación de arranque, correcciones de flota, tabla `conductores` con RLS | Observaciones del Sprint 1 cerradas; estructura de documentos del Sprint 2 |
| 07-10 a 08-10 | Módulo `conductores/` (HU-009) y ampliación de `clientes/` (HU-010) en el backend | Escenarios de aceptación de HU-009 y HU-010 en la API |
| 09-10 | Pantallas de conductores y clientes; pruebas del módulo de personas (HT-06) | HU-009, HU-010 y HT-06 de extremo a extremo |
| 10-10 | **Checkpoint de medio sprint**: reporte de avance individual y recorte de alcance si hace falta | Informe de estado actualizado |
| 11-10 a 14-10 | Motor ACO (HT-07) y generación de rutas (HU-011); tablas `rutas` y `ruta_pedidos`; arquitectura y pruebas de carga (HT-08) | Rutas válidas para 150 pedidos y 15 vehículos en ≤ 45 s |
| 15-10 | Cierre: pruebas de aceptación, cobertura, análisis estático, Pull Request | DoD |
| 16-10 | Inspección | Demostración del sprint |

**Orden de recorte si el tiempo no alcanza** (de lo primero que se sacrificaría a lo último): (1) pruebas de carga con 1,000 pedidos de HT-08, que se documentarían como diseño; (2) pantalla de gestión de clientes, manteniendo la API; (3) afinación del ACO más allá del umbral de rendimiento. Conductores y una primera generación de rutas válida se mantienen como núcleo del sprint.

## 6. Riesgos del Sprint

Se relacionan con el [`03 Registro de riesgos`](../../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Complejidad del motor ACO (HU-011, HT-07 y HT-08 suman 28 SP en Jira) concentrada en poco tiempo | Rutas válidas fuera de plazo | Implementar primero una versión mínima correcta (capacidad y ventanas de tiempo) y afinar después; medir rendimiento desde el primer día |
| Disponibilidad limitada del equipo (RSK-005, IMP-005) | Trabajo concentrado en pocas personas | Dueño explícito por módulo y checkpoint del 10-10 |
| Datos personales de conductores (RSK-009, Ley N° 29733) | Incumplimiento normativo | Consentimiento explícito RN-013 antes de almacenar; cifrado en tránsito y en reposo ya verificados |
| Latencia de la base remota en Supabase (RSK-010) | Pantallas lentas, como el filtro de flota | Menos viajes por petición, filtrado en el cliente para listas pequeñas, índices SQL (HT-08) |
| Interfaz del modo conductor sin auditoría de accesibilidad (RSK-007) | Incumplimiento WCAG 2.1 AA | Ejecutar Lighthouse desde este sprint |

## 7. Evidencias

- Código del backend: [`backend/`](../../../backend/) y del frontend: [`frontend/`](../../../frontend/).
- Estado del sprint anterior: [`01 Sprint 1 Plan de ejecución y estado V_1_5_0`](../Sprint%201/01%20Sprint%201%20Plan%20de%20ejecuci%C3%B3n%20y%20estado%20V_1_5_0.md).
- Entregables de seguimiento: carpeta [`Implementación/`](Implementaci%C3%B3n/).

[← Volver al README Principal](../../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-10-05 | Versión inicial: confirmación del alcance del Sprint 2 contra Jira y la documentación, estado al 05-10-2026 y plan de trabajo | Inciso Aguilar Elizabeth Antonela |
