# 02 Reporte de Variación (Variance Report)

[← Volver al README Principal](../../README.md)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Periodo Reportado** | 17-08-2026 a 22-11-2026 (línea base de 14 semanas) y cierre final en las semanas 15 y 16 |
| **Fecha de Corte** | 2026-11-30 |
| **Fecha de elaboración** | 2026-11-24 |
| **Versión** | 1.0.0 |

---

Este reporte compara lo planificado con lo real en tres dimensiones: cronograma, costo y calidad. La **línea base no se modificó**: las variaciones se muestran tal como ocurrieron. Los valores monetarios y los índices provienen del [`03 Reporte de Análisis de Valor Ganado - EVM`](03%20Reporte%20de%20An%C3%A1lisis%20de%20Valor%20Ganado%20-%20EVM%20V_1_0_0.md), donde también están los supuestos del cálculo.

## 1. Variación de Cronograma

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | 127 Story Points en cuatro sprints de dos semanas, con cierres planificados el 02-10 (Sprint 1, 42 SP), 16-10 (Sprint 2, 41 SP), 30-10 (Sprint 3, 26 SP) y 13-11 (Sprint 4, 18 SP). Planificación inicial entre el 17-08 y el 18-09, y actividad de cierre (calidad y validación) del 14-11 al 22-11. Fin de la línea base: 22-11-2026 (semana 14) |
| **Resultados Reales** | **Cierres en Jira:** Sprint 1 el 01-10, Sprint 2 el 07-10, Sprint 3 el 22-10 y Sprint 4 el 29-10, con sus 18 SP terminados el 23-10. **Inicios en Jira:** 19-09, 05-10, 17-10 y 22-10. SonarQube, OWASP y WCAG hechos el 30-10; Playwright y la escala SUS el 17-11. Los 127 SP aceptados el 23-10. **Cierre final** (siete reportes, video y sustentación): semanas 15 y 16, con la sustentación el 04-12-2026 |
| **Variación Obtenida** | **Línea base: favorable.** Los cuatro sprints se cerraron 1, 9, 8 y 15 días antes de lo planificado, y el alcance completo estuvo aceptado 21 días antes del 13-11. Al 22-11 el SPI es 1.00 y el SV es $0.00; los valores intermedios llegaron a SPI 1.16 (30-10). **Cierre final: desfavorable respecto de las 14 semanas**: el proyecto termina el 04-12 y no el 22-11, es decir, 12 días (2 semanas) después. El Sprint 2 se inició 2 días después de lo planificado (05-10 y no 03-10) |
| **Causa Raíz** | (1) El trabajo de los sprints se terminó en el repositorio antes de lo previsto: el núcleo del Sprint 3 estuvo listo el día 6 de 14 y los 18 SP del Sprint 4 el día 2 de 23, y el equipo actualizaba los estados de Jira en bloque al cerrar cada sprint, por lo que las fechas de Jira pueden ser posteriores a las del trabajo real. (2) Los entregables del cierre final se solicitaron para la evaluación final de la semana 16 y no figuraban en la línea base de 14 semanas, que terminaba con la actividad de cierre y validación del 22-11 |
| **Respuesta Planificada** | El cierre final se gestiona como cambio de alcance **CR-01**, sin modificar la línea base, con las semanas 15 y 16 reservadas para redactar los siete reportes, grabar el video y preparar la demostración. Se verifica el avance cada semana contra la lista de entregables, y se fija el 04-12-2026 como fecha límite. En proyectos futuros, registrar el cierre documental final dentro de la línea base y actualizar el tablero de Jira a diario, no por bloques |

## 2. Variación de Costo

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados** | BAC de **$10,304.00** para 14 semanas (trabajo $9,200.00 + reserva de contingencia $1,104.00, el 12 %): 420 horas asignadas (120 de la líder y 100 de cada uno de los otros tres integrantes) y $0.00 de licencias e infraestructura. Valor planificado acumulado al 22-11: $10,304.00 |
| **Resultados Reales** | Costo real (AC) de la línea base al 22-11: **$8,946.00**, calculado con las horas semanales declaradas (8.2 h la líder y 7 h cada uno de los otros tres, unas 409 horas en 14 semanas) a las tarifas del presupuesto. OPEX ejecutado: $0.00. Proyección del cierre final CR-01 (semanas 15 y 16): $1,278.00. **EAC al 04-12: $10,224.00** |
| **Variación Obtenida** | **Línea base: favorable, CV = +$1,358.00 (13.2 % del BAC)**, CPI 1.15. **Proyección con el cierre final: favorable pero ajustada, VAC = +$80.00 (0.8 %)**, es decir, el proyecto termina por debajo del presupuesto con un margen de unas 3.2 horas de la líder o 4 horas de cualquier otro integrante. **Tendencia desfavorable:** el CPI acumulado baja de 1.31 (16-10) a 1.15 (22-11) y el CPI del periodo 17-10 a 22-11 es 0.88 |
| **Causa Raíz** | (1) Las horas declaradas (29.2 h semanales del equipo) quedaron por debajo de las 30 h semanales presupuestadas (420 h ÷ 14 semanas). (2) La infraestructura se mantuvo en planes gratuitos (Render, Vercel, Supabase). (3) La reserva de contingencia de $1,104.00 no se utilizó en la línea base. (4) La tendencia a la baja se debe a que el costo semanal es constante mientras el trabajo planificado terminó antes: en las últimas semanas se invirtieron horas en validación, documentación y preparación de la sustentación. **Limitación:** no hubo registro de tiempo; las horas son una estimación declarada por cada integrante |
| **Respuesta Planificada** | Vigilar el margen de $80 en las semanas 15 y 16, contando las horas dedicadas al CR-01 cada semana. Si el costo proyectado superara el BAC, se declara en el reporte final con su causa y no se ajusta la línea base. En proyectos futuros, llevar registro de horas (por ejemplo, con el registro de tiempo de Jira) desde el inicio, en lugar de estimarlas al cierre |

## 3. Variación de Calidad

| Métrica / Aspecto | Detalle |
|---|---|
| **Resultados Planificados (Métricas/Criterios)** | Cobertura de pruebas ≥ 80 %; Quality Gate de SonarQube aprobado (fiabilidad, seguridad y mantenibilidad A, duplicación ≤ 3 %, hotspots 100 % revisados); 0 vulnerabilidades críticas de OWASP Top 10; accesibilidad conforme a WCAG 2.2 nivel AA; Lighthouse ≥ 90 y W3C sin errores; generación de 150 pedidos y 15 vehículos en ≤ 45 s (RN-015) y re-optimización en ≤ 30 s (RN-012); usabilidad por encima de la referencia de la industria en la escala SUS (68); aprobación de un compañero en cada Pull Request (criterio 3 del Definition of Done) |
| **Resultados Reales (Defectos/Pruebas)** | **Pruebas:** backend 363 pruebas con 98 % de cobertura (SonarQube: 96.9 %); frontend 147 pruebas de componentes con 80.2 % de cobertura de líneas (SonarQube: 83.0 %); 120 casos de Playwright en tres navegadores (119 aprobados y 1 omitido en WebKit). **SonarQube (30-10):** Quality Gate aprobado (6 de 6 condiciones), 0 bugs, 0 vulnerabilidades, 18 code smells, cobertura del código nuevo 94.3 %. **OWASP Top 10 2025:** 0 vulnerabilidades abiertas, ninguna categoría en «Vulnerable», varias «Bajo revisión». **WCAG 2.2 AA:** 36 de 40 criterios evaluados cumplen (90 %), 3 parciales y 1 sin verificar. **Lighthouse en producción:** rendimiento de 91 a 98, y accesibilidad, buenas prácticas y SEO en 100; W3C con 0 errores. **Rendimiento en Render:** 29.1 s para 150 pedidos y 15 vehículos en el Sprint 2 (unos 30 s después de agregar la matriz de hora punta, IMP-019); re-optimización de 22.2 s (en el servidor) a 27.1 s (medida desde fuera). **Escala SUS:** 73.8 (grado B-) con 10 participantes. **Pull Request:** solo el #60 y el #64 tuvieron la aprobación de un compañero antes de fusionarse |
| **Variación Obtenida** | **Favorable** en cobertura (+18 puntos en el backend; +0.2 puntos en el frontend con Vitest), Quality Gate, tiempos de rutas (29.1 s contra 45 s; hasta 27.1 s contra 30 s), Lighthouse y SUS (+5.8 puntos sobre 68). **Desfavorable o parcial en:** (1) 4 de 40 criterios de WCAG sin cumplir del todo (teclado en los marcadores del mapa, avisos que desaparecen a los 3.5 s, mensajes de error genéricos y contraste de componentes sin medir); (2) brechas de revisión manual de OWASP abiertas (política de seguridad de contenido, bloqueo de `requirements.txt` con sumas de verificación y MFA obligatorio para el administrador); (3) el criterio de aprobación de Pull Request incumplido en casi todos los de los Sprints 3 y 4; (4) el rendimiento de Lighthouse en Mapa y Pedidos llegó a 85 en el Sprint 2, por debajo de 90; (5) en el primer análisis (23-10) SonarQube registró 8 bugs, 16 vulnerabilidades y 292 code smells, con calificaciones E en seguridad y fiabilidad |
| **Causa Raíz** | (1) La cobertura del frontend se mantuvo apenas sobre el mínimo porque las pruebas de extremo a extremo con Playwright (33 al cierre del Sprint 3 y 120 en el Sprint 4) no entran en la medición de cobertura. (2) Las brechas de OWASP y WCAG son controles de revisión manual que se priorizaron detrás de las funcionalidades y quedaron como plan de acciones. (3) El rendimiento de Lighthouse en Sprint 2 se debió a la latencia de la API en Render gratuito (cerca de 1 s por petición, IMP-016), no al código de la interfaz. (4) Los hallazgos de SonarQube se acumularon porque el análisis se ejecutó por primera vez al cierre del Sprint 3, no desde el inicio. (5) Los Pull Request se fusionaban sin aprobación por la disponibilidad limitada del equipo y la concentración del trabajo en pocas personas (IMP-005 e IMP-025). Defectos reales encontrados y corregidos: CORS rechazaba PATCH en producción (la entrega desde la vista del conductor fallaba) y una vulnerabilidad alta nueva en `undici`, detectada por el propio CI |
| **Respuesta Planificada** | Durante el proyecto se aplicó la aprobación de un compañero en los Pull Request #60 y #64 y la guía de primeros pasos con preguntas frecuentes (17-11), derivada del SUS. Las demás mejoras de la retrospectiva del Sprint 4 son opcionales y quedan para una siguiente etapa (ver el [`06`](06%20Reporte%20Final%20del%20Proyecto%20V_1_0_0.md)). Para WCAG: lista navegable de paradas, avisos que se puedan cerrar, mensajes de error por campo y prueba con un lector de pantalla. En proyectos futuros, ejecutar SonarQube desde el primer sprint |

### Resumen de las tres variaciones

| Dimensión | Planificado | Real | Variación | Estado |
|---|---|---|---|---|
| Cronograma (línea base) | Fin el 22-11-2026 (semana 14) | 127 SP aceptados el 23-10; línea base completa | SV $0.00 al corte; adelanto de 15 a 21 días en los sprints | Verde |
| Cronograma (cierre final) | Sin tiempo en la línea base | Semanas 15 y 16, sustentación el 04-12 | 12 días después de la línea base | Ámbar |
| Costo | BAC $10,304.00 | AC $8,946.00 (línea base); EAC $10,224.00 | CV +$1,358.00 (13.2 %); VAC +$80.00 (0.8 %) | Verde (ámbar en la proyección) |
| Calidad | Criterios de la columna «Planificados» | Mayoría cumplida; brechas parciales en WCAG, OWASP y aprobación de PR | Favorable en pruebas, rendimiento y usabilidad; abierto en controles manuales | Ámbar |

---

[← Volver al README Principal](../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-24 | Versión inicial: variación de cronograma, costo y calidad de la línea base de 14 semanas y del cierre final (CR-01), con corte al 30-11-2026 | Inciso Aguilar Elizabeth Antonela |
