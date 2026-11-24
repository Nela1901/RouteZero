# 06 Reporte Final del Proyecto (Final Project Report)

[← Volver al README Principal](../../README.md)

## Metadatos

| Campo | Detalle |
|---|---|
| **Proyecto** | RouteZero — Optimizador de rutas sostenibles (empresa ficticia Andina Reparto S.A.C., Huancayo) |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Fecha de Cierre** | Sustentación final del 04-12-2026 (semana 16). La línea base de 14 semanas terminó el 22-11-2026 |
| **Fecha de elaboración** | 2026-11-24 (corte de datos: 2026-11-30) |
| **Versión** | 1.0.0 |

---

## 1. Descripción General del Proyecto

RouteZero es una plataforma web que optimiza las rutas de reparto de Andina Reparto S.A.C., una empresa ficticia de distribución con sede en El Tambo, Huancayo. Resuelve el Problema de Ruteo de Vehículos con Ventanas de Tiempo (VRPTW) con consideraciones ambientales (Green VRP) mediante un motor de optimización con metaheurística de colonia de hormigas (ACO), y muestra las rutas sobre un mapa interactivo con congestión por horas punta. El sistema incluye autenticación con MFA, gestión de flota, conductores, clientes y pedidos, re-optimización ante incidentes, una vista móvil para el conductor y un módulo de sostenibilidad (dashboard de CO₂, reporte PDF y plan de compensación).

El problema que motivó el proyecto, según el [`02. Acta de constitución`](../01%20Inicio/02.%20Acta%20de%20constituci%C3%B3n%20V_1_0_0.md) (28-08-2026), son la congestión en la Av. Ferrocarril, la Av. Giráldez y la Calle Real en horas punta, los costos de combustible y mantenimiento, las emisiones de CO₂ evitables y el incumplimiento de ventanas de tiempo. El sistema está desplegado en Render (backend) y Vercel (frontend), sobre PostgreSQL en Supabase.

**Enfoque híbrido.** El **inicio y la planificación** (17-08 a 18-09) y el **cierre final** fueron predictivos, con documentos y fechas fijas. El **desarrollo** fue adaptativo, en cuatro sprints de dos semanas con 127 Story Points en Jira.

---

## 2. Resumen de Desempeño

### 2.1 Alcance (predictivo y adaptativo)

- **Objetivos y criterios de éxito (Acta de constitución):**

| # | Objetivo | Criterio de éxito | Resultado | Evidencia |
|---|---|---|---|---|
| O-01 | MVP funcional | Al menos 70 % de los requisitos funcionales implementados | **Cumplido: 11 de 11 requisitos funcionales (100 %)**, cada uno con al menos una historia completada en Jira (127 de 127 SP) | Planes de ejecución de los Sprints 1 a 4 |
| O-02 | Algoritmo de optimización | Rutas en ≤ 45 s para 150 pedidos | **Cumplido:** 29.1 s en Render con 150 pedidos y 15 vehículos (unos 30 s con la matriz de hora punta); re-optimización en 22.2 a 27.1 s contra el límite de 30 s | Sprints 2 y 3 |
| O-03 | Mapa interactivo | Muestra rutas, puntos de entrega y nivel de tráfico | **Cumplido:** mapa con trazado por calles, congestión por horas punta e incidentes | Sprint 3 |
| O-04 | Reportes de sostenibilidad | PDF descargable desde el dashboard | **Cumplido:** dashboard, reporte PDF de hasta 30 días (7.5 s en Render) y plan de compensación | Sprint 4 |
| O-05 | Estándares de calidad | W3C, ISO/IEC 25010, OWASP Top 10, WCAG y Green Software, verificables con herramientas | **Cumplido con brechas:** W3C 0 errores; OWASP 2025 sin vulnerabilidades abiertas; WCAG 2.2 AA con 36 de 40 criterios evaluados; Green Software con cálculo SWDM; ISO/IEC 25010 documentada en el documento de estándares de la Inspección 04 | Sprints 3 y 4 e Inspección 04 |

- **Variaciones, causas e impacto.**
  - **Algoritmo:** el acta preveía iniciar con un algoritmo genético simple; se implementó ACO (el genético quedó como opción secundaria). No afectó el criterio de éxito.
  - **Alcance aceptado:** los 127 Story Points se mantuvieron en el plan. En Jira, las cinco historias técnicas del Sprint 1 (22 SP) entraron al sprint el 01-10, y HT-07 (2 SP) se marcó terminada el 06-10 aunque su segundo escenario se verificó el 20-10 con HU-012.
  - **Cambio de alcance CR-01:** cierre final (siete reportes, video y sustentación), fuera de la línea base.
  - **Norma citada:** el «DS 033-2012-MTC» no existe; la norma es el DS 033-2001-MTC (IMP-014).
- **Trabajo predictivo y adaptativo.** Predictivo: documentos de inicio y planificación (acta, visión, requisitos, base de datos, presupuesto y riesgos) y cierre final. Adaptativo: los cuatro sprints, con revisión y retrospectiva al cierre de cada uno.

### 2.2 Calidad

- **Requisitos y criterios de aceptación.** Cobertura ≥ 80 %; Quality Gate de SonarQube aprobado; 0 vulnerabilidades críticas de OWASP; WCAG 2.2 AA; Lighthouse ≥ 90 y W3C sin errores; RN-015 (≤ 45 s) y RN-012 (≤ 30 s); SUS por encima de 68.
- **Resultados de verificación y validación.** Backend: 363 pruebas, 98 % de cobertura. Frontend: 147 pruebas de componentes (80.2 %) y 120 casos de Playwright en tres navegadores (119 aprobados, 1 omitido). SonarQube: Quality Gate aprobado, 0 bugs y 0 vulnerabilidades. Lighthouse en producción: rendimiento de 91 a 98 y 100 en accesibilidad, buenas prácticas y SEO. Validación con personas reales de los tres roles (administración, operación y conducción): escala SUS 73.8 (B-) con 10 participantes. Detalle en [`02 Reporte de Variación`](02%20Reporte%20de%20Variaci%C3%B3n%20V_1_0_0.md).
- **Requisitos eximidos o variaciones.**
  - **RN-004 (restricción por placa)** queda configurable y **desactivada**: la norma real, el DS 033-2001-MTC, no trae una tabla por dígito de placa.
  - **WCAG:** 4 criterios sin cumplir del todo (teclado en marcadores del mapa, avisos de 3.5 s, mensajes de error genéricos y contraste de componentes sin medir); sin prueba con lector de pantalla.
  - **OWASP:** brechas de revisión manual abiertas (política de seguridad de contenido, bloqueo de dependencias y MFA obligatorio para el administrador); el DNI de los conductores se guarda en texto plano, protegido por consentimiento y acceso solo del administrador.
  - **Disponibilidad del 99.5 %** (requisito no funcional): no se midió; el plan gratuito de Render se apaga tras un periodo sin tráfico y la primera petición tardó 51.7 s (IMP-027).

### 2.3 Cronograma

Semana 1: 17-08-2026. Fechas de Jira para los sprints. Fuentes de las fechas reales: gráficos de trabajo pendiente de Jira y documentos de estado.

| Hito / Entrega | Enfoque | Fecha Planificada | Fecha Real | Variación / Impacto |
|---|---|---|---|---|
| H-01 Inicio y planificación (análisis, diseño de BD, presupuesto y riesgos) | Predictivo | Semana 3 (hasta el 06-09) | Documentos iniciales entre el 28-08 y el 10-09; inicio del Sprint 1 el 19-09 | Unos 4 días después del hito del acta, sin impacto en los sprints |
| Sprint 1: autenticación, flota y pedidos (42 SP) | Adaptativo | Cierre 02-10 | Cierre 01-10; historias de usuario terminadas el 28-09 | 1 día antes |
| H-02 Flota, pedidos y algoritmo base | Adaptativo | Semana 7 (hasta el 04-10) | Flota y pedidos el 28-09 y 01-10; algoritmo base (ACO) el 06-10 | Algoritmo 2 días después del hito |
| Sprint 2: personas y motor ACO (41 SP) | Adaptativo | 03-10 a 16-10 | Inicio 05-10, cierre 07-10 | Cierre 9 días antes (inicio 2 días después) |
| Sprint 3: re-optimización y mapa (26 SP) | Adaptativo | 17-10 a 30-10 | 17-10 a 22-10 | Cierre 8 días antes |
| H-03 Mapa, dashboard y reportes PDF | Adaptativo | Semana 11 (hasta el 01-11) | Mapa el 22-10; dashboard y PDF el 23-10 | Unos 9 días antes |
| Sprint 4: sostenibilidad (18 SP) | Adaptativo | 31-10 a 13-11 | 22-10 a 29-10; historias terminadas el 23-10 | Inicio 9 días antes, cierre 15 días antes |
| Actividad de cierre y validación (SonarQube, OWASP, WCAG, Playwright y SUS) | Predictivo | 14-11 a 22-11 | 30-10 (tres actividades) y 17-11 (dos); Inspección 05 el 20-11 | Dentro de la línea base |
| H-04 Fin de la línea base | Predictivo | Semana 14 (22-11) | 22-11 | Sin variación (SPI 1.00) |
| Cierre final CR-01 y H-05 Presentación final | Predictivo | Semana 15 (según el acta) | Semanas 15 y 16; sustentación el 04-12 (semana 16) | 12 días después de la línea base; la fecha la fija el cronograma de evaluación del curso |

Los cierres de Jira son posteriores al trabajo real: el equipo actualizaba los estados de las historias en bloque al final de cada sprint.

### 2.4 Costo

- **Presupuesto aprobado (y rango de tolerancia):** BAC de **$10,304.00** ($9,200.00 de trabajo y $1,104.00 de reserva de contingencia). El presupuesto no definió un rango de tolerancia; se toma como criterio de éxito **no superar el BAC**.
- **Costo final real del proyecto:** línea base, **$8,946.00** (14 semanas). Con el cierre final CR-01 (semanas 15 y 16), la estimación a la conclusión es **$10,224.00**. Las horas son estimaciones declaradas por cada integrante, no registros de tiempo.
- **Análisis de variaciones e impacto:** CV de la línea base +$1,358.00 (CPI 1.15); VAC proyectado +$80.00 (0.8 %). La reserva de contingencia no se usó en la línea base; el cierre final consume el ahorro y deja un margen de $80. Detalle en [`03 Reporte de Análisis de Valor Ganado - EVM`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md).

---

## 3. Resumen de Riesgos, Incidentes e Impedimentos

Los identificadores IMP corresponden a los registros de impedimentos de cada sprint en `docs/03 Implementación`; los RSK, al [`03 Registro de riesgos`](../02%20Planificaci%C3%B3n/03%20Registro%20de%20riesgos%20V_1_0_0.md).

| ID / Descripción | Tipo | Impacto Real | Respuesta Aplicada |
|---|---|---|---|
| **RSK-001** Complejidad del ACO mayor a la estimada | Riesgo (materializado en parte) | La primera medición en Render fue de 64 s contra el límite de 45 s (IMP-010) | Perfilado: el cuello de botella era guardar fila por fila en la base remota; con INSERT en bloque bajó a 29.1 s |
| **IMP-005 / RSK-005** Disponibilidad limitada y trabajo concentrado en pocas personas | Impedimento (abierto) | Implementación concentrada en una persona durante los cuatro sprints; autoría poco visible en el repositorio | Responsables por ítem en Jira, aporte declarado por integrante en revisiones y retrospectivas; dos compañeros aprobaron el PR #64 |
| **IMP-001** «Enable automatic RLS» de Supabase deja las tablas nuevas sin acceso | Impedimento (resuelto) | Horas de depuración en el Sprint 1 | Políticas permisivas explícitas para tablas organizacionales; checklist de RLS pendiente |
| **IMP-004** Versión de SQLAlchemy distinta en Render | Impedimento (resuelto) | El backend fallaba al desplegar, un día antes de la inspección del Sprint 1 | Tope superior de versión en `requirements.txt` |
| **IMP-006** `token_version` desajustado por el hook de Supabase | Impedimento (resuelto) | Sesiones con «Token revocado» la noche previa a una inspección | Restablecer `token_version` de la cuenta afectada |
| **IMP-013 / IMP-016 / IMP-019** CPU de 0.1 y latencia de Render gratuito | Impedimento (abierto, heredado) | Re-optimización de 22.2 a 27.1 s contra 30 s; unos 2 s por petición | Presupuesto de 25 s del motor, medición en Render; mejora posible con más CPU o matrices reutilizadas |
| **IMP-017** Cambio de contrato de la API que rompió el mapa en producción | Incidente (resuelto) | Mapa caído en producción, detectado por la auditoría de Lighthouse | Prueba de regresión y regla de actualizar todos los consumidores antes de cambiar un contrato |
| **IMP-014** Norma citada inexistente (DS 033-2012-MTC) | Incidente (resuelto) | Cita errónea en varios documentos | Verificación con el texto oficial y corrección a DS 033-2001-MTC |
| **IMP-024** Sin datos reales de la empresa para supuestos de sostenibilidad | Impedimento (abierto) | Cifras de combustible, meta de CO₂ y árboles son supuestos | Variables de entorno declaradas como supuestos; validación pendiente con la empresa |
| **IMP-025** Pull Request fusionados sin la aprobación de un compañero | Incidente (parcialmente resuelto) | Criterio 3 del Definition of Done sin evidencia en casi todos los PR de los Sprints 3 y 4 | Aprobación registrada en el #60 y el #64; acción de la retrospectiva para exigirla antes de cada merge |
| **IMP-027** Arranque en frío de Render (51.7 s) | Impedimento (abierto) | La primera petición, o la demostración, espera casi un minuto | Calentar Render antes de cada demostración |
| **IMP-028 / IMP-029** Despliegue automático sin esperar pruebas; vulnerabilidad de `picomatch` sin parche (solo desarrollo) | Impedimento (abierto) | Riesgo de desplegar con pruebas fallidas; fallo del CI con auditoría estricta | Flujo de despliegue condicionado a pruebas en verde; auditoría de producción separada de la de desarrollo |

---

## 4. Evaluación del Éxito y Cierre

- **Satisfacción de los interesados (Stakeholders).** No existe un cliente real: Andina Reparto S.A.C. es una empresa ficticia, y los interesados se representaron con participantes de los tres roles del sistema. La escala SUS de **10 participantes dio 73.8 (grado B-)**: el sistema se percibe fácil, consistente y confiable; su debilidad es la curva de entrada (ítems de ayuda y aprendizaje con 1.4 de 4), por lo que se aplicó una guía de primeros pasos con preguntas frecuentes el 17-11. Queda pendiente volver a medir el SUS (meta: promedio de al menos 73.8). La validación de los supuestos de sostenibilidad con una empresa real (IMP-024) tampoco se realizó.
- **Satisfacción y reconocimiento del equipo.** Cada integrante declaró haberse sentido entre bien y muy bien durante los cuatro sprints y haber dedicado a la semana las horas indicadas en el [`03 Reporte de Análisis de Valor Ganado - EVM`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md) (8.2 h la líder y 7 h cada uno de los otros tres). El estado de ánimo por sprint figura en [`05 Radiadores de Información`](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md). La exigencia de entregar bien en cada sprint fue alta y el equipo supo manejarla, cumpliendo todos los sprints. El trabajo se concentró en pocas personas (IMP-005): es el principal punto de mejora en la dinámica del equipo. El reconocimiento individual se documenta con hechos declarados en la revisión y la retrospectiva de cada sprint.
- **Transición operativa y cierre administrativo.** Es un proyecto académico, sin transición a una empresa real ni contratos con terceros (todos los servicios son gratuitos). Lo que se entrega queda así: sistema desplegado en Render y Vercel; repositorio público con `backend/` y `frontend/` separados y `.gitignore` que excluye credenciales, entornos virtuales y dependencias; documentación técnica y de gestión por sprint en `docs/`; siete reportes de cierre en `docs/04 Cierre`; video en `docs/05 Video proyecto`; guía de primeros pasos dentro de la aplicación. No aplica el acompañamiento de 30 días de operación ni el pago a proveedores.
- **Mejoras opcionales para una siguiente etapa.** Surgidas de la retrospectiva del Sprint 4: datos reales de la flota, reutilización de matrices entre peticiones, checklist de políticas RLS, factores de hora punta con fuente citada, refuerzos de seguridad de OWASP (política de seguridad de contenido, bloqueo de dependencias y MFA obligatorio para el administrador) y una nueva medición con la escala SUS (opcional). Durante el proyecto se aplicaron la guía de primeros pasos (17-11) y la aprobación de un compañero en los Pull Request #60 y #64.
- **Conclusión.** El proyecto **cumple los cinco objetivos del acta**: 11 de 11 requisitos funcionales, rutas en 29.1 s contra 45 s, mapa, reportes y estándares verificados con herramientas. Terminó la línea base en 14 semanas con un CPI de 1.15 y un SPI de 1.00, y cierra el 04-12-2026 con una estimación de $10,224.00 contra $10,304.00 de presupuesto. Los puntos abiertos (brechas parciales de WCAG y OWASP, aprobación de Pull Request, medición de horas y concentración del trabajo) están declarados con su respuesta.

---

## 5. Coherencia con los Documentos Previos

No hubo re-baseline: el acta de constitución, el presupuesto, el plan de Jira y los documentos de cada sprint **se mantienen en sus versiones**, y los reportes de cierre se miden contra esa línea base. Las diferencias que existen entre estos documentos y los datos finales de Jira son las siguientes, y todas están explicadas:

| Tema | Lo que dicen los documentos previos | Lo que muestra Jira al cierre | Explicación |
|---|---|---|---|
| Periodo del Sprint 4 | 22-10 a 13-11-2026 (periodo planificado en Jira) | Terminado el 23-10 y finalizado el 29-10 | Se **adelantó**: cierre 15 días antes del fin planificado ([`03`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md), sección 0) |
| Sprints 2 y 3 | Fin planificado el 16-10 y el 30-10 | Finalizados el 07-10 y el 22-10 | Se **adelantaron** 9 y 8 días (sección 2.3) |
| Story Points del Sprint 2 | Revisión del sprint: 39 de 41, con HT-07 parcial | 41 de 41 desde el 06-10 | Jira marcó HT-07 al terminar el motor; su segundo escenario se verificó el 20-10 con HU-012 ([`03`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md), limitaciones) |
| Alcance del Sprint 1 | Plan: 42 SP y 13 ítems desde el inicio | Alcance de 20 SP que pasa a 42 el 01-10 | Las cinco historias técnicas se cargaron al sprint el 01-10 ([`05`](05%20Radiadores%20de%20Informaci%C3%B3n%20V_1_0_0.md), burnup) |
| Presentación final | Acta de constitución: semana 15 | Sustentación el 04-12-2026 (semana 16) | La fecha la fija el cronograma de evaluación del curso |

---

[← Volver al README Principal](../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-24 | Versión inicial: reporte final del proyecto con desempeño predictivo y adaptativo, hitos con fechas reales, riesgos e impedimentos y evaluación del éxito | Inciso Aguilar Elizabeth Antonela |
