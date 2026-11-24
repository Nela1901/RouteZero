# 03 Reporte de Análisis de Valor Ganado - EVM (Earned Value Analysis Report)

[← Volver al README Principal](../../README.md)

## Metadatos

| Campo | Detalle |
|---|---|
| **Nombre del Proyecto** | RouteZero — Optimizador de rutas sostenibles |
| **Empresa ficticia** | Andina Reparto S.A.C. |
| **Líder del Proyecto** | Inciso Aguilar Elizabeth Antonela |
| **Integrantes** | Inciso Aguilar Elizabeth Antonela, Espinoza Tiza Yago Imanol, Guerra Lozano Keen, Uscuvilca Ramos Abraham Luis |
| **Presupuesto hasta la Conclusión (BAC)** | **USD $10,304.00** (trabajo $9,200.00 + reserva de contingencia $1,104.00, el 12 %) |
| **Estado General** | **VERDE** en la línea base (SPI 1.00 y CPI 1.15 al 22-11-2026); **ÁMBAR** en la proyección con el cierre final (CR-01), que deja un margen de solo $80 |
| **Fecha de corte** | 2026-11-30 (cierre de la semana 15). La línea base terminó el 22-11-2026 (semana 14) |
| **Fecha de elaboración** | 2026-11-24 |
| **Versión** | 1.0.0 |

---

## 0. Cómo se calculó (supuestos de la medición)

Este reporte compara el trabajo realizado contra la **línea base aprobada**, sin modificarla. No se hizo ningún re-baseline: el BAC y el cronograma de 14 semanas siguen siendo los de [`04 Presupuesto del proyecto V_1_1_0`](../02%20Planificaci%C3%B3n/04%20Presupuesto%20del%20proyecto%20V_1_1_0.md) y [`02 Artefactos Jira V_1_1_0`](../02%20Planificaci%C3%B3n/02%20Artefactos%20Jira%20V_1_1_0.md).

| Elemento | Criterio usado |
|---|---|
| **BAC** | $10,304.00: el presupuesto total del documento de presupuesto, que ya incluye la reserva de contingencia de $1,104.00 (12 % de $9,200.00). Es la misma cifra que citan los informes de estado |
| **Semana 1** | Lunes 17-08-2026. La línea base cubre las semanas 1 a 14 (17-08 a 22-11-2026); la semana 15 empieza el 23-11 y la 16 el 30-11 |
| **Paquetes de trabajo** | El BAC se reparte según los días de calendario de cada fase en las 14 semanas (98 días): **A** Inicio y planificación, 17-08 a 18-09 (33 días, predictivo): $3,469.71. **B** Desarrollo por sprints, 19-09 a 13-11 (56 días, adaptativo): $5,888.00. **C** Actividad de cierre y validación, 14-11 a 22-11 (9 días): $946.29 |
| **PV** | Valor acumulado planificado a cada fecha de corte. En B se reparte según los Story Points planificados por sprint: 42, 41, 26 y 18 (total 127), con corte en el fin planificado de cada sprint (02-10, 16-10, 30-10 y 13-11) |
| **EV** | A: 100 % al 18-09 (documentos de inicio y planificación). B: Story Points aceptados ÷ 127. C: cinco actividades de igual peso (SonarQube Cloud, OWASP Top 10 2025 y WCAG 2.2, hechas el 30-10; Playwright con monitoreo de producción y escala SUS, hechas el 17-11). Fuentes: tablero y gráficos de Jira (vigente según la documentación), y planes de ejecución y documentos de evaluación de cada sprint |
| **AC** | Horas semanales **declaradas por cada integrante** × tarifa del presupuesto, por los días de calendario transcurridos (ver la tabla siguiente). **Es una estimación declarada, no una medición con registro de tiempo**: el proyecto no llevó registro de horas |
| **Story Points aceptados** | Sprint 1: 42 (cerrado el 01-10). Sprint 2: 41, cerrado el 07-10 (el gráfico de trabajo pendiente de Jira registra las seis incidencias terminadas el 06-10 a las 12:02 a. m., HT-07 incluida; su segundo escenario, la re-optimización en 30 s o menos, se verificó el 20-10 con HU-012, ver la sección 6). Sprint 3: 26 (cerrado el 22-10). Sprint 4: 18, terminados el 23-10 y cerrado en Jira el 29-10 |

### Costo semanal declarado por el equipo

| Integrante | Rol | Horas por semana | Tarifa (USD/h) | Costo semanal | AC en 14 semanas |
|---|---|---|---|---|---|
| Inciso Aguilar Elizabeth Antonela | Arquitecta de Software / Project Manager | 8.2 | $25 | $205.00 | $2,870.00 |
| Espinoza Tiza Yago Imanol | Ingeniero de IA e Integración | 7 | $22 | $154.00 | $2,156.00 |
| Guerra Lozano Keen | Desarrollador Backend | 7 | $20 | $140.00 | $1,960.00 |
| Uscuvilca Ramos Abraham Luis | Desarrollador Frontend | 7 | $20 | $140.00 | $1,960.00 |
| **Equipo** | | **29.2** | | **$639.00** | **$8,946.00** |

En 14 semanas son unas 409 horas, frente a las 420 horas asignadas en el presupuesto (97 %). El costo diario es de $639 ÷ 7 = $91.29.

---

## 1. Métricas de Desempeño EVM

**Periodo actual:** 17-10-2026 a 22-11-2026 (Sprints 3 y 4 y actividad de cierre). **Acumulado periodo anterior:** corte del 16-10-2026 (fin planificado del Sprint 2). **Acumulado periodo actual:** corte del 22-11-2026, fin de la línea base.

| Métrica / Indicador | Periodo actual | Acumulado periodo actual | Acumulado periodo anterior |
|---|---|---|---|
| **Valor Planificado (PV)** | $2,986.22 | $10,304.00 | $7,317.78 |
| **Valor Ganado (EV)** | $2,986.22 | $10,304.00 | $7,317.78 |
| **Costo Real (AC)** | $3,377.57 | $8,946.00 | $5,568.43 |
| **Variación del Cronograma (SV = EV − PV)** | $0.00 | $0.00 | $0.00 |
| **Variación del Costo (CV = EV − AC)** | −$391.35 | +$1,358.00 | +$1,749.35 |
| **Índice de Desempeño del Cronograma (SPI = EV / PV)** | 1.00 | 1.00 | 1.00 |
| **Índice de Desempeño del Costo (CPI = EV / AC)** | 0.88 | 1.15 | 1.31 |

### Interpretación

- **Cronograma.** Al 16-10 el SPI era 1.00: los Sprints 1 y 2 estaban cerrados con sus 83 Story Points aceptados en Jira. En el periodo siguiente el equipo terminó los 127 Story Points el 23-10, antes del 13-11 planificado, de modo que entre el 30-10 y el 13-11 el SPI superó 1.00 (trabajo adelantado). Al 22-11 el SPI es 1.00: todo lo planificado en las 14 semanas está entregado.
- **Costo, acumulado.** Con un CPI de 1.15 se obtienen $1.15 de trabajo por cada dólar gastado: el costo acumulado ($8,946.00) quedó $1,358.00 por debajo del BAC.
- **Costo, tendencia.** El CPI acumulado **baja** de 1.31 (16-10) a 1.15 (22-11), y el CPI del periodo actual es 0.88. La causa es que el costo semanal es constante ($639) mientras que el trabajo planificado se completó antes de lo previsto: en las últimas semanas el equipo siguió invirtiendo horas en validación, documentación y preparación de la sustentación. Es una tendencia que debe vigilarse: si el gasto continuara sin trabajo de línea base pendiente, el CPI seguiría bajando.
- **Historial por corte** (todas las fechas de corte de la línea base):

| Corte | PV | EV | AC | SV | CV | SPI | CPI | % planificado | % ganado | % gastado |
|---|---|---|---|---|---|---|---|---|---|---|
| 18-sep (fin de la planificación) | $3,469.71 | $3,469.71 | $3,012.43 | $0.00 | $457.28 | 1.00 | 1.15 | 33.7 % | 33.7 % | 29.2 % |
| 02-oct (fin planificado Sprint 1) | $5,416.93 | $5,416.93 | $4,290.43 | $0.00 | $1,126.50 | 1.00 | 1.26 | 52.6 % | 52.6 % | 41.6 % |
| 16-oct (fin planificado Sprint 2) | $7,317.78 | $7,317.78 | $5,568.43 | $0.00 | $1,749.35 | 1.00 | 1.31 | 71.0 % | 71.0 % | 54.0 % |
| 30-oct (fin planificado Sprint 3) | $8,523.19 | $9,925.49 | $6,846.43 | $1,402.30 | $3,079.06 | 1.16 | 1.45 | 82.7 % | 96.3 % | 66.4 % |
| 13-nov (fin planificado Sprint 4) | $9,357.71 | $9,925.49 | $8,124.43 | $567.78 | $1,801.06 | 1.06 | 1.22 | 90.8 % | 96.3 % | 78.8 % |
| 22-nov (fin de la línea base) | $10,304.00 | $10,304.00 | $8,946.00 | $0.00 | $1,358.00 | 1.00 | 1.15 | 100.0 % | 100.0 % | 86.8 % |

---

## 2. Porcentajes de Avance Acumulado (Respecto al BAC)

Al corte de la línea base (22-11-2026):

- **Porcentaje Planificado (PV / BAC):** 100.0 %
- **Porcentaje Ganado (EV / BAC):** 100.0 %
- **Porcentaje Gastado (AC / BAC):** 86.8 %

Se gastó el 86.8 % del presupuesto para completar el 100 % del trabajo planificado, cuando se esperaba estar al 100 %. Los $1,358.00 de diferencia incluyen los $1,104.00 de reserva de contingencia, que no se utilizó.

---

## 3. Análisis de Desviaciones

- **Causa raíz de la variación del cronograma.**
  - **Al 16-10 (SV $0.00):** el avance coincide con lo planificado. Una salvedad documentada: Jira marcó HT-07 como terminada el 06-10, pero su segundo escenario (re-optimización en 30 s o menos ante un incidente) dependía de HU-012 y se verificó el 20-10, dentro del Sprint 3 (Plan de ejecución del Sprint 3). Esos 2 SP valen $92.73 del paquete B (2 × $5,888.00 ÷ 127) y no alteran las conclusiones.
  - **Del 30-10 al 13-11 (SV favorable):** el núcleo del Sprint 3 terminó el día 6 de 14 y los 18 SP del Sprint 4 estuvieron completos el 23-10, 21 días antes del fin planificado. Además, SonarQube, OWASP y WCAG quedaron hechos y documentados el 30-10, dentro del Sprint 4 y antes de las pruebas de Playwright y la escala SUS (17-11).
- **Impacto en el cronograma.** Ninguno negativo: la línea base se completó el 22-11 como estaba planificado, con trabajo adelantado en el medio. Los entregables del cierre final (semanas 15 y 16) no pertenecen a esta línea base y se tratan en la sección 5.
- **Causa raíz de la variación del costo.** El costo es **menor** que el presupuestado por tres razones: (1) las horas semanales declaradas (29.2 h para el equipo) quedaron por debajo de las 30 h semanales presupuestadas (420 h ÷ 14 semanas); (2) la infraestructura se mantuvo en planes gratuitos (Render, Vercel y Supabase), con un OPEX de $0.00; (3) la reserva de contingencia no se consumió. La **tendencia** descrita en la sección 1 es el único punto de atención.
- **Impacto en el presupuesto.** Favorable en la línea base: sobran $1,358.00. Ese margen se usa en gran parte para el cierre final (sección 5).

---

## 4. Estimaciones a la Conclusión (EAC)

### 4.1 Fórmulas estándar al corte de la línea base (22-11-2026)

Con CPI = 10,304.00 ÷ 8,946.00 = 1.1518 y SPI = 1.0000:

- **Fórmula 1 (EAC = BAC / CPI):** 10,304.00 ÷ 1.1518 = **$8,946.00**
- **Fórmula 2 (EAC = BAC / (CPI × SPI)):** 10,304.00 ÷ (1.1518 × 1.0000) = **$8,946.00**
- **Fórmula 3 (EAC = AC + [(BAC − EV) / (CPI × SPI)]):** 8,946.00 + [(10,304.00 − 10,304.00) ÷ 1.1518] = **$8,946.00**

Las tres coinciden porque **no queda trabajo de la línea base por hacer** (BAC − EV = 0) y el SPI es 1.00: la proyección de lo que falta es cero y el costo final de la línea base es el costo real acumulado. Para ver cómo se comportan las fórmulas cuando sí hay trabajo pendiente, estos son los mismos cálculos en dos cortes anteriores:

| Corte | CPI | SPI | EAC 1: BAC / CPI | EAC 2: BAC / (CPI × SPI) | EAC 3: AC + (BAC − EV) / (CPI × SPI) |
|---|---|---|---|---|---|
| 30-oct | 1.45 | 1.16 | $7,108 | $6,103 | $7,071 |
| 13-nov | 1.22 | 1.06 | $8,434 | $7,952 | $8,417 |

En ambos cortes las tres proyecciones quedaron por debajo del BAC, y el costo final real de la línea base ($8,946) las supera en los dos casos porque el gasto semanal continuó cuando el trabajo ya estaba hecho.

### 4.2 EAC seleccionado y justificación

**EAC seleccionado: $10,224.00** = costo real de la línea base ($8,946.00) + costo proyectado del cierre final CR-01 ($1,278.00).

**Justificación.** Las tres fórmulas estándar solo proyectan el trabajo que estaba en la línea base, y ese trabajo está terminado. Lo que falta por gastar corresponde a las semanas 15 y 16, que no estaban en el presupuesto: el cierre final (siete reportes, video y sustentación) exigido por la consigna de la evaluación final. Por eso la proyección razonable es la **fórmula 3 más el costo proyectado de ese cambio** (EAC = $8,946.00 + $1,278.00). El costo del CR-01 se calcula con el ritmo semanal declarado: 2 semanas × $639.00 = $1,278.00.

| Concepto | Valor |
|---|---|
| BAC (presupuesto con contingencia) | $10,304.00 |
| Costo real de la línea base (semanas 1 a 14) | $8,946.00 |
| Costo proyectado del cierre final CR-01 (semanas 15 y 16) | $1,278.00 |
| **EAC seleccionado** | **$10,224.00** |
| Variación proyectada contra el BAC (VAC = BAC − EAC) | **+$80.00** (queda 0.8 % por debajo del presupuesto) |
| Porcentaje del BAC proyectado | 99.2 % |

---

## 5. Cierre final (CR-01): semanas 15 y 16

- **Qué es.** La consigna de la evaluación final pide siete reportes de cierre, un video y la sustentación del viernes 04-12-2026. Ese trabajo no estaba en la línea base de 14 semanas, por lo que se registra como cambio de alcance **CR-01**. **La línea base no se modificó** y todo el reporte la mide contra el BAC original.
- **Costo de las dos semanas.** AC de la semana 15 (23-11 a 29-11): $639.00. AC proyectado de la semana 16 (30-11 a 06-12): $639.00.
- **AC acumulado al corte del 30-11-2026** (semanas 1 a 15): $9,585.00 = $8,946.00 de la línea base + $639.00 de la semana 15. Es el 93.0 % del BAC.
- **Estado de los datos de la semana 15.** El reporte se elaboró el 24-11-2026. El costo de la semana 15 se calcula con las horas semanales declaradas y se confirma el 30-11-2026; si el equipo trabaja más o menos horas, el AC se actualiza en una nueva versión.
- **El margen es estrecho: $80.** Equivale a unas 3.2 horas adicionales de la líder (a $25) o 4 horas adicionales de cualquier otro integrante (a $20) en las dos semanas. Si se supera, el proyecto cerraría por encima del BAC, y el reporte final lo declarará con su causa raíz. El avance del CR-01 (entregables terminados sobre nueve: siete reportes, video y sustentación) se medirá con su propio EV al cierre, en el reporte final.

---

## 6. Limitaciones

- **Las horas son estimaciones declaradas por cada integrante.** Cada uno las confirmó por escrito en el grupo del equipo: unas 7 horas por semana Yago, Keen y Abraham, y aproximadamente 8 horas la líder (el cálculo usa 8.2, dentro de esa aproximación). No existe registro de horas trabajadas. El AC se calculó con horas semanales aproximadas y se aplicó de forma uniforme a todos los días de calendario desde el 17-08-2026.
- **El reparto del BAC por paquetes** se basó en los días de calendario de cada fase y el peso de las cinco actividades del paquete C se tomó igual; son decisiones de medición declaradas, no datos del presupuesto original.
- **El EV de B depende de los Story Points** de Jira. Las fechas de Jira difieren de las del plan (Artefactos Jira V_1_1_0): el Sprint 2 se inició en Jira el 05-10 a las 6:35 p. m. y se finalizó el 07-10, y el Sprint 4, previsto hasta el 13-11, se inició el 22-10 a las 9:33 p. m., tuvo sus 18 SP terminados el 23-10 a las 2:59 p. m. y se finalizó el 29-10 a las 7:26 p. m.
- **Alcance del Sprint 1 en Jira.** El plan (Artefactos Jira V_1_1_0) compromete 42 SP y 13 ítems desde el inicio. El gráfico de Jira muestra que el sprint se inició el 19-09 con 8 historias de usuario (20 SP) y que las cinco historias técnicas HT-01 a HT-05 (22 SP) se agregaron al sprint el 01-10 entre las 7:46 p. m. y las 7:51 p. m., con el sprint finalizado ese mismo día a las 8:02 p. m. Este reporte mide contra el plan (42 SP): para Jira el alcance creció 110 % durante el sprint, pero respecto a la línea base aprobada no hay variación de alcance.
- **Actualización del tablero en bloque.** En los cuatro sprints Jira registra las historias como terminadas todas a la vez (28-09, 06-10, 22-10 y 23-10) y no de forma gradual. El equipo terminaba el trabajo en el repositorio y actualizaba los estados al cierre, de modo que las fechas de finalización de Jira pueden ser posteriores a las del trabajo real. El avance real está en el historial de git y en los planes de ejecución de cada sprint.
- **HT-07 y los documentos del Sprint 2.** El Plan de ejecución del Sprint 2 (V_1_8_0) y la Revisión del Sprint 2 (V_1_6_0) registran 39 de 41 SP con HT-07 parcial, mientras que Jira la marcó terminada el 06-10 junto con las otras cinco incidencias. Este reporte sigue a Jira, que es el tablero vigente, y deja la salvedad por escrito; la verificación completa de HT-07 ocurrió el 20-10.
- **El CPI alto** (por encima de 1.0 en todo el proyecto) se debe en parte a que el costo se mide por tiempo transcurrido mientras el valor se mide por trabajo entregado, y el equipo entregó antes de lo planificado.

---

[← Volver al README Principal](../../README.md)

## Historial de Control de Cambios

| Versión | Fecha | Cambio realizado | Responsable |
|---|---|---|---|
| V_1_0_0 | 2026-11-24 | Versión inicial: análisis de valor ganado de la línea base (14 semanas) con corte al 30-11-2026, tres fórmulas de EAC, EAC seleccionado con el cierre final CR-01 y limitaciones | Inciso Aguilar Elizabeth Antonela |
